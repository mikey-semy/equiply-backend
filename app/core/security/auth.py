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
    async def protected_route(user: UserCredentialsSchema = Depends(get_current_user)):
        return {"message": f"Hello, {user.username}!"}
    ```
"""

import logging
from fastapi import Request, Depends
from fastapi.security import OAuth2PasswordBearer
from dishka.integrations.fastapi import FromDishka, inject

from app.core.security import TokenManager
from app.core.exceptions import TokenError, TokenInvalidError, TokenMissingError, InvalidCredentialsError
from app.services.v1.auth.service import AuthService
from app.schemas import UserCredentialsSchema
from app.core.settings import settings

logger = logging.getLogger(__name__)

# Создаем экземпляр OAuth2PasswordBearer для использования с Depends
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.AUTH_URL,
    auto_error=True,
    scheme_name="OAuth2PasswordBearer"
)


class AuthenticationManager:
    """
    Менеджер аутентификации пользователей.

    Этот класс предоставляет методы для работы с аутентификацией,
    включая проверку токенов и получение данных текущего пользователя.

    Методы:
        get_current_user: Получает данные текущего пользователя по токену
        validate_token: Проверяет валидность токена и извлекает полезную нагрузку
    """

    @staticmethod
    @inject
    async def get_current_user(
        request: Request,
        token: str = Depends(oauth2_scheme),
        auth_service: FromDishka[AuthService] = None
    ) -> UserCredentialsSchema:
        """
        Получает данные текущего аутентифицированного пользователя.

        Эта функция проверяет JWT токен, переданный в заголовке Authorization,
        декодирует его, и получает пользователя из системы по идентификатору
        в токене (sub).

        Args:
            request: Запрос FastAPI, содержащий заголовки HTTP
            token: Токен доступа, извлекаемый из заголовка Authorization
            auth_service: Сервис аутентификации (внедряется Dishka)

        Returns:
            UserCredentialsSchema: Схема данных текущего пользователя

        Raises:
            TokenInvalidError: Если токен отсутствует, недействителен или истек
        """
        logger.debug("Обработка запроса аутентификации с заголовками: %s", request.headers)
        logger.debug("Начало получения данных пользователя")
        logger.debug("Получен токен: %s", token)

        if not token:
            logger.debug("Токен отсутствует в запросе")
            raise TokenMissingError()

        try:
            payload = TokenManager.verify_token(token)

            user_email = TokenManager.validate_payload(payload)

            user = await auth_service.get_user_by_identifier(user_email)

            if not user:
                logger.debug("Пользователь с email %s не найден", user_email)
                raise InvalidCredentialsError()

            user_schema = UserCredentialsSchema.model_validate(user)
            logger.debug("Пользователь успешно аутентифицирован: %s", user_schema)

            return user_schema

        except TokenError:
        # Перехватываем все ошибки токенов и пробрасываем дальше
            raise
        except Exception as e:
            logger.debug("Ошибка при аутентификации: %s", str(e))
            raise TokenInvalidError() from e


# Для совместимости с существующим кодом и простоты использования
get_current_user = AuthenticationManager.get_current_user
