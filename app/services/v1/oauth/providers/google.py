import secrets
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse

from app.core.exceptions import OAuthTokenError
from app.core.integrations.cache.oauth import OAuthRedisStorage
from app.schemas import (GoogleTokenDataSchema, GoogleUserDataSchema,
                         OAuthParamsSchema, OAuthProvider)
from app.services.v1.oauth.base import BaseOAuthProvider
from app.services.v1.auth.service import AuthService
from app.services.v1.users.service import UserService
from app.services.v1.register.service import RegisterService

from ..data_manager import OAuthDataManager

class GoogleOAuthProvider(BaseOAuthProvider):
    """
    OAuth провайдер для Google.

    Особенности:
    - Использует строковый формат ID пользователя
    - Поддерживает OpenID Connect (id_token)
    - Стандартный OAuth2 flow с state для CSRF защиты

    Flow:
    1. Получение auth_url с state параметром
    2. Редирект пользователя на страницу входа Google
    3. Получение code и state от Google
    4. Обмен code на access_token и id_token
    5. Получение данных пользователя через access_token
    """

    def __init__(
        self,
        data_manager: OAuthDataManager,
        auth_service: AuthService,
        register_service: RegisterService,
        redis_storage: OAuthRedisStorage
    ):
        """
        Инициализация Google OAuth провайдера.

        Args:
            data_manager: Менеджер данных пользователя
            auth_service: Сервис аутентификации
            register_service: Сервис регистрации
            redis_storage: Хранилище для временных данных OAuth
        """
        super().__init__(
            provider=OAuthProvider.GOOGLE.value,
            data_manager=data_manager,
            auth_service=auth_service,
            register_service=register_service,
            redis_storage=redis_storage
        )

    async def get_auth_url(self) -> RedirectResponse:
        """
        Формирование URL для OAuth авторизации через Google.

        Генерирует случайный state для CSRF защиты и сохраняет в Redis.
        Добавляет необходимые OAuth параметры в URL.

        Returns:
            RedirectResponse: URL для перенаправления на страницу входа Google
        """
        state = secrets.token_urlsafe()
        await self.redis_storage.set(f"google_state_{state}", state)

        params = OAuthParamsSchema(
            client_id=self.settings.client_id,
            redirect_uri=await self._get_callback_url(),
            scope=self.settings.scope,
            state=state,
        )

        auth_url = f"{self.settings.auth_url}?{urlencode(params.model_dump())}"
        return RedirectResponse(url=auth_url)

    async def get_token(
        self, code: str, state: str = None, device_id: str = None
    ) -> GoogleTokenDataSchema:
        """
        Получение токена от Google по коду авторизации.

        Проверяет наличие кода и обменивает его на access_token и id_token.
        Поддерживает OpenID Connect flow.

        Args:
            code: Код авторизации от Google
            state: Параметр state для проверки CSRF
            device_id: Не используется

        Returns:
            GoogleTokenDataSchema: Токен доступа и связанные данные

        Raises:
            OAuthTokenError: При отсутствии кода или ошибке от Google API
        """

        if not code:
            raise OAuthTokenError(self.provider, "Не передан код авторизации")

        token_data = await self._get_token_data(code, state)
        return GoogleTokenDataSchema(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "bearer"),
            expires_in=token_data["expires_in"],
            id_token=token_data["id_token"],
            scope=token_data["scope"],
        )

    async def get_user_info(self, token: str) -> GoogleUserDataSchema:
        """
        Получение данных пользователя через Google API.

        Использует стандартный эндпоинт Google для получения
        информации о пользователе. Возвращает данные в формате GoogleUserDataSchema.

        Args:
            token: Токен доступа от Google

        Returns:
            GoogleUserDataSchema: Данные пользователя в унифицированном формате
        """
        user_data = await super().get_user_info(token)
        self.logger.debug("Данные пользователя (google provider): %s", user_data)
        return user_data

    def _get_provider_id(self, user_data: GoogleUserDataSchema) -> str:
        """
        Преобразование ID пользователя в строковый формат.
        Google всегда возвращает строковый ID.
        """
        return str(user_data.id)
