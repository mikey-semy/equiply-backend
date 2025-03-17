from pydantic import EmailStr
from app.schemas.v1.base import BaseRequestSchema
from app.schemas.v1.auth.responses import TokenResponseSchema
from app.core.settings import settings

class OAuthResponseSchema(TokenResponseSchema):
    """
    Схема ответа OAuth авторизации.

    Attributes:
        access_token: Токен доступа
        token_type: Тип токена (bearer)
        refresh_token: Токен обновления токена
        redirect_uri: Путь для перенаправления после авторизации (для пользователя)
    """

    refresh_token: str | None = None
    redirect_uri: str = "/"

class OAuthProviderResponseSchema(BaseRequestSchema): # TODO: Изменить схему наследования
    """
    Класс для ответа OAuth авторизации. Используется для получения токена

    Attributes:
        access_token: Токен доступа
        token_type: Тип токена (bearer)
        expires_in: Время жизни токена в секундах
    """

    access_token: str
    token_type: str = settings.TOKEN_TYPE
    expires_in: int

class YandexTokenDataSchema(OAuthProviderResponseSchema):
    """
    Класс для данных токена OAuth авторизации через Яндекс

    Attributes:
        refresh_token: Токен обновления токена
        scope: Область доступа
    """

    refresh_token: str
    scope: str


class GoogleTokenDataSchema(OAuthProviderResponseSchema):
    """
    Класс для данных токена OAuth авторизации через Google

    Attributes:
        id_token: Токен идентификации
        scope: Область доступа
    """

    id_token: str
    scope: str


class VKTokenDataSchema(OAuthProviderResponseSchema):
    """
    Класс для данных токена OAuth авторизации через VK

    Attributes:
        user_id: Идентификатор пользователя
        email: Электронная почта пользователя
        state: Состояние
        scope: Область доступа
    """

    user_id: int
    email: EmailStr | None = None
    state: str | None = None
    scope: str | None = None
