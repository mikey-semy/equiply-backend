import logging
import secrets
from abc import ABC, abstractmethod
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse

from app.core.exceptions import OAuthConfigError, OAuthUserDataError
from app.core.integrations.cache.oauth import OAuthRedisStorage
from app.core.integrations.http.oauth import OAuthHttpClient
from app.core.security import PasswordHasher, TokenManager
from app.core.settings import settings
from app.schemas import (OAuthConfigSchema, OAuthParamsSchema, OAuthProvider,
                         OAuthProviderResponseSchema, OAuthResponseSchema,
                         OAuthTokenParamsSchema, OAuthUserDataSchema,
                         OAuthUserSchema, RegistrationSchema,
                         UserCredentialsSchema)
from app.services.v1.auth.service import AuthService
from app.services.v1.oauth.handlers import PROVIDER_HANDLERS
from app.services.v1.users.service import UserService
from app.services.v1.register.service import RegisterService


class BaseOAuthProvider(ABC, PasswordHasher, TokenManager):
    """
    Базовый класс для OAuth провайдеров.

    Flow аутентификации:
    1. Получение auth_url для редиректа пользователя на провайдера
    2. Получение от провайдера токена по коду аутентификации
    3. Получение от провайдера данных пользователя по токену через специализированный handler
    4. Поиск/создание пользователя в базе данных
    5. Генерация токенов для аутентификации пользователя

    Attributes:
        provider: Тип OAuth провайдера (yandex, google, vk)
        settings: Конфигурация провайдера из настроек
        user_handler: Специализированный обработчик данных пользователя
        http_client: HTTP клиент для запросов к API провайдера
        auth_service: Сервис аутентификации
        user_service: Сервис работы с пользователями
        redis_storage: Хранилище для временных данных OAuth

    Usage:
        # В роутерах:
        @router.get("/oauth/{provider}") # 1
        async def oauth_login(provider: OAuthProvider):
            return await OAuthService(db_session).get_oauth_url(provider)

        @router.get("/oauth/{provider}/callback") # 2, 3, 4, 5
        async def oauth_callback(provider: OAuthProvider, code: str):
            return await OAuthService(db_session).authenticate(provider, code)

        # В сервисе:
        async def get_oauth_url(self, provider: OAuthProvider) -> str:
            oauth_provider = self.get_provider(provider)
            return await oauth_provider.get_auth_url() # 1

        async def authenticate(self, provider: OAuthProvider, code: str) -> OAuthResponse:
            oauth_provider = self.get_provider(provider)
            token = await oauth_provider.get_token(code) # 2
            user_data = await oauth_provider.get_user_info(token["access_token"]) # 3
            return await oauth_provider.authenticate(user_data) # 4, 5
    """

    def __init__(
        self,
        provider: OAuthProvider,
        auth_service: AuthService,
        user_service: UserService,
        register_service: RegisterService,
        redis_storage: OAuthRedisStorage,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.provider = provider
        self.settings = OAuthConfigSchema(**settings.OAUTH_PROVIDERS[provider])
        self.user_handler = PROVIDER_HANDLERS[provider]
        self.auth_service = auth_service
        self.user_service = user_service
        self.register_service = register_service
        self.redis_storage = redis_storage
        self.http_client = OAuthHttpClient()

    async def authenticate(self, user_data: OAuthUserDataSchema) -> OAuthResponseSchema:
        """
        Аутентификация через OAuth провайдер.

        Flow:
        1. Поиск пользователя по типизированному provider_id
        2. Если не найден - поиск по валидированному email
        3. Если не найден - создание пользователя с нормализованными данными
        4. Генерация токенов

        Args:
            user_data: Типизированные данные от handler'а провайдера (YandexUserData/GoogleUserData/VKUserData)

        Returns:
            OAuthResponse: Токены и redirect_uri
        """
        user = await self._find_user(user_data)
        if not user:
            user = await self._create_user(user_data)
        return await self._create_tokens(user)

    async def _find_user(
        self, user_data: OAuthUserDataSchema
    ) -> UserCredentialsSchema | None:
        """
        Поиск существующего пользователя по данным OAuth.

        Flow:
        1. Получение типизированного provider_id через handler
        2. Поиск по ID провайдера ({provider}_id)
        3. Если не найден - поиск по валидированному email

        Args:
            user_data: Типизированные данные пользователя от handler'а

        Returns:
            UserCredentialsSchema | None: Найденный пользователь или None
        """
        provider_id = self._get_provider_id(user_data)
        user = await self.user_service.data_manager.get_item_by_field(
            f"{self.provider}_id", provider_id
        )
        if not user:
            user = await self.user_service.data_manager.get_item_by_field(
                "email", self._get_email(user_data)
            )
        return user

    def _get_provider_id(self, user_data: OAuthUserDataSchema) -> int:
        """
        Получение ID пользователя от провайдера.

        Преобразует строковый ID из типизированных данных в числовой формат.
        Каждый handler гарантирует наличие валидного id.

        Args:
            user_data: Типизированные данные от handler'а

        Returns:
            int: Числовой ID пользователя

        Raises:
            ValueError: Если ID невалиден
        """
        try:
            return int(user_data.id)
        except (ValueError, TypeError):
            raise ValueError(
                f"ID провайдера '{user_data.id}' невозможно преобразовать в целое число"
            )

    def _get_email(self, user_data: OAuthUserDataSchema) -> str:
        """
        Получение email пользователя.

        Каждый handler валидирует email через EmailStr.
        YandexHandler использует default_email
        GoogleHandler проверяет verified_email
        VKHandler логирует отсутствие email

        Args:
            user_data: Типизированные данные от handler'а

        Returns:
            str: Валидированный email

        Raises:
            OAuthUserDataError: Если email отсутствует
        """
        if not user_data.email:
            raise OAuthUserDataError(
                self.provider, "Email не найден в данных пользователя"
            )
        return user_data.email

    async def _create_user(
        self, user_data: OAuthUserDataSchema
    ) -> UserCredentialsSchema:
        """
        Создание пользователя через OAuth.

        Flow:
        1. Получение нормализованных данных от handler'а
        2. Формирование OAuthUserSchema с валидированными полями
        3. Создание пользователя с типизированным provider_id
        4. Логирование результата

        Args:
            user_data: Типизированные данные от handler'а

        Returns:
            UserCredentialsSchema: Созданный пользователь
        """
        email = self._get_email(user_data)
        username_base = email.split("@")[0]
        username = f"{username_base}_{self.provider}_{secrets.token_hex(4)}"

        avatar=getattr(user_data, "avatar", None)
        self.logger.debug(
            "Данные аватара для пользователя %s: %s",
            email,
            avatar
        )

        oauth_user = OAuthUserSchema(
            username=username,
            first_name=getattr(user_data, "first_name", username_base),
            last_name=getattr(user_data, "last_name", ""),
            email=email,
            password=secrets.token_hex(16),
            avatar=avatar,
            **{f"{self.provider}_id": self._get_provider_id(user_data)},
        )

        self.logger.debug(
            "Данные для создания пользователя: %s",
            oauth_user.model_dump()
        )

        user_credentials = await self.register_service.create_oauth_user(
            RegistrationSchema(**oauth_user.model_dump())
        )

        self.logger.debug(
            "Созданный пользователь (user_credentials): %s", vars(user_credentials)
        )

        return user_credentials

    async def _create_tokens(self, user: UserCredentialsSchema) -> OAuthResponseSchema:
        """
        Генерация access и refresh токенов для OAuth аутентификации.

        Flow:
        1. Создание access токена через AuthService
        2. Генерация refresh токена
        3. Формирование ответа с redirect_uri

        Args:
            user: Схема пользователя для создания токенов

        Returns:
            OAuthResponse: Токены и URI для редиректа

        Usage:
            tokens = await self._create_tokens(user_schema)
            # Returns: OAuthResponse(
            #    access_token="eyJ...",
            #    refresh_token="eyJ...",
            #    redirect_uri="/home"
            # )
        """
        access_token = await self.auth_service.create_token(user)
        refresh_token = TokenManager.generate_token(
            {
                "sub": user.email,
                "type": "refresh",
                "expires_at": TokenManager.get_token_expiration(),
            }
        )
        return OAuthResponseSchema(
            **access_token.model_dump(),
            refresh_token=refresh_token,
            redirect_uri=settings.OAUTH_SUCCESS_REDIRECT_URI,
        )

    def _validate_config(self) -> None:
        """
        Валидация конфигурации провайдера.

        Проверяет обязательные поля для работы с API провайдера:
        - client_id (str/int в зависимости от провайдера)
        - client_secret (str)

        Raises:
            OAuthConfigError: Если отсутствуют обязательные поля
        """
        if not self.settings.client_id or not self.settings.client_secret:
            raise OAuthConfigError(self.provider, ["client_id", "client_secret"])

    async def _get_token_data(self, code: str, state: str = None) -> dict:

        token_params = OAuthTokenParamsSchema(
            client_id=self.settings.client_id,
            client_secret=self.settings.client_secret,
            code=code,
            redirect_uri=str(await self._get_callback_url()),
        )

        return await self.http_client.get_token(
            self.settings.token_url, token_params.model_dump()
        )

    async def _get_callback_url(self) -> str:
        """
        Генерирует callback URL для OAuth провайдера.

        Этот метод использует конфигурацию приложения для формирования полного URL,
        который включает в себя текущий домен, версию API и имя провайдера.

        Пример использования:
            url = await provider._get_callback_url()
            # Возвращает: https://domain.com/api/v1/oauth/google/callback

        Returns:
            str: Полный валидный URL для callback эндпоинта провайдера.
        """
        return self.settings.callback_url.format(provider=self.provider)

    @abstractmethod
    async def get_auth_url(self) -> RedirectResponse:
        """
        Получение URL для OAuth авторизации.

        #! Этот метод должен быть реализован в каждом наследуемом классе.

        Базовая реализация:
        1. Валидирует конфигурацию провайдера
        2. Формирует базовые OAuth параметры
        3. Строит URL для авторизации

        Специальные механизмы авторизации:
        - VK: Использует PKCE (code_verifier + code_challenge)
            code_verifier = secrets.token_urlsafe(64)
            code_challenge = base64(sha256(code_verifier))
            params = VKOAuthParams(code_challenge=code_challenge)

        Usage:
            @router.get("/oauth/{provider}")
            async def oauth_login(provider: str):
                return await oauth_provider.get_auth_url()

            # VK Provider
            async def get_auth_url(self):
                params = VKOAuthParams(
                    code_challenge=self._generate_code_challenge(),
                    state=secrets.token_urlsafe()
                )
                await self.redis_storage.save_verifier(params.state, code_verifier)
                return RedirectResponse(url=f"{self.auth_url}?{urlencode(params)}")

            # Генерация кода challenge для OAuth2 (используется для VK).
            def _generate_code_challenge(self, verifier: str) -> str:
                return base64.urlsafe_b64encode(
                    hashlib.sha256(verifier.encode()).digest()
                ).decode().rstrip('=')

        Returns:
            RedirectResponse: Редирект на URL авторизации провайдера
        """
        self._validate_config()

        params = OAuthParamsSchema(
            client_id=self.settings.client_id,
            redirect_uri=await self._get_callback_url(),
            scope=self.settings.scope,
        )

        auth_url = f"{self.settings.auth_url}?{urlencode(params.model_dump())}"
        return RedirectResponse(url=auth_url)

    @abstractmethod
    async def get_token(
        self, code: str, state: str = None, device_id: str = None
    ) -> OAuthProviderResponseSchema:
        """
        Получение токена доступа от OAuth провайдера.

        #! Этот метод должен быть реализован в каждом наследуемом классе.

        Flow:
        1. Формирование параметров запроса
        2. Обработка state параметра если требуется
        3. Отправка запроса на получение токена
        4. Обработка ошибок

        Args:
            code: Код авторизации от провайдера
            state: Параметр state для безопасности (опционально)

        Returns:
            OAuthProviderResponse: Токен доступа и связанные данные

        Raises:
            OAuthInvalidGrantError: Если код авторизации невалиден
            OAuthTokenError: При других ошибках получения токена

        Usage:
            token_data = await provider.get_token(code, state)
            user_info = await provider.get_user_info(token_data.access_token)
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user_info(
        self, token: str, client_id: str = None
    ) -> OAuthUserDataSchema:
        """
        Получение данных пользователя от OAuth провайдера.

        #! Этот метод должен быть реализован в каждом наследуемом классе.

        Flow:
        1. Запрос к API провайдера с токеном
        2. Преобразование ответа через типизированный handler (YandexHandler/GoogleHandler/VKHandler)
        3. Валидация обязательных полей
        4. Нормализация имен пользователя

        Args:
            token: Токен доступа от провайдера
            client_id: ID приложения (опционально)

        Returns:
            OAuthUserData: Типизированные данные пользователя (YandexUserData/GoogleUserData/VKUserData)

        Raises:
            OAuthUserDataError: Если отсутствуют обязательные поля
        """
        user_data = await self.http_client.get_user_info(
            self.settings.user_info_url, token, client_id=client_id
        )
        return await self.user_handler(user_data)
