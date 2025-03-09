"""
Модуль зависимостей для аутентификации.

Содержит функции-зависимости для работы с токенами и текущим пользователем.
"""

import logging
from fastapi import Request, Depends
from fastapi.security import OAuth2PasswordBearer
from dishka.integrations.fastapi import FromDishka, inject

from app.core.security import TokenManager
from app.core.exceptions import TokenInvalidError
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

@inject
async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),  # Используем стандартный Depends для отображения замочка
    auth_service: FromDishka[AuthService] = None
) -> UserCredentialsSchema:
    """
    Получает данные текущего пользователя.

    Args:
        request: Запрос FastAPI
        token: Токен доступа (извлекается из заголовка Authorization)
        auth_service: Сервис аутентификации (внедряется Dishka)

    Returns:
        Данные текущего пользователя.
    """
    logger.debug("Все заголовки запроса: %s", request.headers)
    logger.debug("Начало получения текущего пользователя")
    logger.debug("Получен токен: %s", token)

    if not token:
        logger.debug("Токен отсутствует в запросе")
        raise TokenInvalidError()

    try:
        # Валидация токена и получение пользователя
        payload = TokenManager.decode_token(token)
        user_email = payload.get("sub")

        if not user_email:
            logger.debug("Email пользователя отсутствует в токене")
            raise TokenInvalidError()

        # Получение пользователя
        user = await auth_service.get_user_by_identifier(user_email)

        if not user:
            logger.debug("Пользователь не найден")
            raise TokenInvalidError()

        # Преобразуем модель в схему
        user_schema = UserCredentialsSchema.model_validate(user)
        logger.debug("Пользователь успешно получен: %s", user_schema)

        return user_schema

    except Exception as e:
        logger.debug("Ошибка при получении пользователя: %s", str(e))
        raise TokenInvalidError() from e
