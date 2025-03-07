"""
Модуль зависимостей для аутентификации.

Содержит функции-зависимости для работы с токенами и текущим пользователем.

Usage:

    from fastapi import APIRouter
    from dishka.integrations.fastapi import FromDishka, inject

    from app.schemas import UserCredentialsSchema
    from app.core.dependencies import get_current_user

    router = APIRouter(prefix="/protected", tags=["Protected"])

    @router.get("/me")
    @inject
    async def get_me(current_user: FromDishka[UserCredentialsSchema] = get_current_user):
        #Получить данные текущего пользователя
        return current_user
"""

import logging
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from dishka.integrations.fastapi import FromDishka, inject
from app.core.security import TokenManager
from app.core.exceptions import TokenInvalidError
from app.services.v1.auth.service import AuthService
from app.schemas import UserCredentialsSchema


logger = logging.getLogger(__name__)

@inject
async def get_current_user(
    request: Request,
    oauth2_schema: FromDishka[OAuth2PasswordBearer],
    auth_service: FromDishka[AuthService]
) -> UserCredentialsSchema:
    """
    Получает данные текущего пользователя.

    Args:
        request: Запрос FastAPI
        oauth2_schema: Схема OAuth2 (внедряется Dishka)
        auth_service: Сервис аутентификации (внедряется Dishka)

    Returns:
        Данные текущего пользователя.
    """
    logger.debug("Все заголовки запроса: %s", request.headers)
    logger.debug("Начало получения текущего пользователя")

    # Получаем токен из заголовка Authorization
    token = await oauth2_schema(request)
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