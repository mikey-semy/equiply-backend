"""
Модуль аутентификации и авторизации пользователей.

Этот модуль предоставляет компоненты для проверки подлинности
и авторизации пользователей в приложении FastAPI с использованием
JWT токенов и интеграции с Dishka.

Основные компоненты:
- OAuth2PasswordBearer: схема безопасности для документации OpenAPI
- get_current_user: функция-зависимость для получения текущего пользователя

Примеры использования:

1. В маршрутах FastAPI с использованием стандартных зависимостей:
    ```
    @router.get("/protected")
    async def protected_route(user: CurrentUserSchema = Depends(get_current_user)):
        return {"message": f"Hello, {user.username}!"}
    ```
"""

import logging

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import (InvalidCredentialsError, TokenError,
                                 TokenInvalidError, TokenMissingError)
from app.core.security import TokenManager, CookieManager
from app.core.settings import settings
from app.schemas import CurrentUserSchema, UserCredentialsSchema
from app.services.v1.auth.service import AuthService

logger = logging.getLogger(__name__)

# Создаем экземпляр OAuth2PasswordBearer для использования с Depends
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.AUTH_URL,
    scheme_name="OAuth2PasswordBearer",
    description="Bearer token",
    auto_error=False,
)


class AuthenticationManager:
    """
    Менеджер аутентификации пользователей.

    Этот класс предоставляет методы для работы с аутентификацией,
    включая проверку токенов и получение данных текущего пользователя.

    Методы:
        get_current_user: Получает данные текущего пользователя по токену
        validate_token: Проверяет валидность токена и извлекает полезную нагрузку
        extract_token_from_request: Извлекает токен из запроса (заголовок или cookies)
    """

    @staticmethod
    def extract_token_from_request(request: Request, header_token: str = None) -> str:
        """
        Извлекает токен из запроса - сначала из заголовка Authorization, затем из cookies.

        Args:
            request: Запрос FastAPI, содержащий заголовки HTTP и cookies
            header_token: Токен из заголовка Authorization (если есть)

        Returns:
            str: Найденный токен

        Raises:
            TokenMissingError: Если токен не найден ни в заголовке, ни в cookies
        """
        # Сначала пробуем получить токен из заголовка Authorization
        if header_token:
            logger.debug("Токен найден в заголовке Authorization")
            return header_token

        # Если токена нет в заголовке, проверяем cookies
        access_token_cookie = request.cookies.get(CookieManager.ACCESS_TOKEN_KEY)

        if access_token_cookie:
            logger.debug("Токен найден в cookies")
            return access_token_cookie

        # Если токен не найден ни в заголовке, ни в cookies
        logger.debug("Токен не найден ни в заголовке Authorization, ни в cookies")
        raise TokenMissingError()

    @staticmethod
    @inject
    async def get_current_user(
        request: Request,
        token: str = Depends(oauth2_scheme),
        auth_service: FromDishka[AuthService] = None,
    ) -> UserCredentialsSchema:
        """
        Получает данные текущего аутентифицированного пользователя.

        Эта функция проверяет JWT токен, переданный в заголовке Authorization или cookies,
        декодирует его, и получает пользователя из системы по идентификатору
        в токене (sub).

        Args:
            request: Запрос FastAPI, содержащий заголовки HTTP и cookies
            token: Токен доступа, извлекаемый из заголовка Authorization (может быть None)
            auth_service: Сервис аутентификации (внедряется Dishka)

        Returns:
            UserCredentialsSchema: Схема данных текущего пользователя

        Raises:
            TokenInvalidError: Если токен отсутствует, недействителен или истек
        """
        logger.debug(
            "Обработка запроса аутентификации с заголовками: %s", request.headers
        )
        logger.debug("Начало получения данных пользователя")
        logger.debug("Получен токен из заголовка: %s", token)

        try:
            # Извлекаем токен из запроса (заголовок или cookies)
            actual_token = AuthenticationManager.extract_token_from_request(request, token)
            logger.debug("Используемый токен: %s", actual_token[:50] + "..." if actual_token else "None")

            # Проверяем и декодируем токен
            payload = TokenManager.verify_token(actual_token)

            user_email = TokenManager.validate_payload(payload)

            user = await auth_service.get_user_by_identifier(user_email)

            if not user:
                logger.debug("Пользователь с email %s не найден", user_email)
                raise InvalidCredentialsError()

            user_schema = UserCredentialsSchema.model_validate(user)
            logger.debug("Пользователь успешно аутентифицирован: %s", user_schema)

            current_user = CurrentUserSchema(
                id=user_schema.id,
                username=user_schema.username,
                email=user_schema.email,
                role=user_schema.role,
                is_active=user_schema.is_active,
                is_verified=user_schema.is_verified,
            )

            return current_user

        except TokenError:
            # Перехватываем все ошибки токенов и пробрасываем дальше
            raise
        except Exception as e:
            logger.debug("Ошибка при аутентификации: %s", str(e))
            raise TokenInvalidError() from e


# Для совместимости с существующим кодом и простоты использования
get_current_user = AuthenticationManager.get_current_user
