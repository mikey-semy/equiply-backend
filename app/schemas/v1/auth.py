"""
Схемы для аутентификации и управления пользователями.
"""

from pydantic import Field, EmailStr

from app.core.settings import settings

from .base import BaseInputSchema, BaseResponseSchema


class AuthSchema(BaseInputSchema):
    """
    Схема аутентификации пользователя.

    Attributes:
        username: Идентификатор пользователя (имя, email или телефон)
        password: Пароль пользователя
    """
    username: str = Field(
        description="Имя пользователя, email или телефон в формате +7 (XXX) XXX-XX-XX"
    )
    password: str = Field(
        min_length=8,
        description="Пароль должен быть минимум 8 символов",
    )

class TokenSchema(BaseInputSchema):
    """
    Схема токена.

    Args:
        access_token (str): Токен доступа.
        token_type (str): Тип токена.
    """

    access_token: str
    token_type: str = settings.TOKEN_TYPE


class TokenResponseSchema(BaseResponseSchema):
    """
    Схема ответа с токеном доступа

    Swagger UI ожидает строго определенный формат ответа для OAuth2 password flow
    (access_token и token_type обязательны, другие поля игнорируются)

    Docs:
        https://swagger.io/docs/specification/authentication/oauth2/
        (Из РФ зайти можно только через VPN - санкции)

        https://developer.zendesk.com/api-reference/sales-crm/authentication/requests/#token-request

    Attributes:
        access_token: Токен доступа.
        token_type: Тип токена.
        success: Признак успешной авторизации
        message: Сообщение об успешной авторизации
    """

    access_token: str
    token_type: str = settings.TOKEN_TYPE
    success: bool = True
    message: str = "Авторизация успешна"

class ForgotPasswordSchema(BaseInputSchema):
    """Схема для запроса сброса пароля"""
    email: EmailStr

class PasswordResetResponseSchema(BaseResponseSchema):
    """Схема ответа на запрос сброса пароля"""
    success: bool = True
    message: str = "Инструкции по сбросу пароля отправлены на ваш email"

class PasswordResetConfirmSchema(BaseInputSchema):
    """Схема для установки нового пароля"""
    password: str

class PasswordResetConfirmResponseSchema(BaseResponseSchema):
    """Схема ответа на установку нового пароля"""
    success: bool = True
    message: str = "Пароль успешно изменен"