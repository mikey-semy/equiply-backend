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
    Схема токена авторизации.

    Используется для передачи токена доступа клиенту после успешной авторизации.

    Attributes:
        access_token: Токен доступа для авторизации в системе.
        token_type: Тип токена авторизации (обычно "bearer").
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

class LogoutResponseSchema(BaseResponseSchema):
    """
    Схема ответа для выхода из системы.
    
    Отправляется клиенту после успешного завершения сессии и выхода пользователя из системы.
    
    Attributes:
        success: Признак успешного выхода из системы.
        message: Информационное сообщение о результате операции.
    """
    success: bool = True
    message: str = "Выход выполнен успешно!"

class ForgotPasswordSchema(BaseInputSchema):
    """
    Схема для запроса сброса пароля.
    
    Используется когда пользователь забыл пароль и хочет его восстановить.
    
    Attributes:
        email: Электронная почта пользователя, на которую будет отправлена инструкция по сбросу пароля.
    """
    email: EmailStr

class PasswordResetResponseSchema(BaseResponseSchema):
    """
    Схема ответа на запрос сброса пароля.
    
    Отправляется после успешной обработки запроса на сброс пароля.
    
    Attributes:
        success: Признак успешной обработки запроса.
        message: Информационное сообщение о результате операции и дальнейших действиях.
    """
    success: bool = True
    message: str = "Инструкции по сбросу пароля отправлены на ваш email"

class PasswordResetConfirmSchema(BaseInputSchema):
    """
    Схема для установки нового пароля.
    
    Используется после подтверждения запроса на сброс пароля для установки нового пароля пользователя.
    
    Attributes:
        password: Новый пароль пользователя, который заменит предыдущий.
    """
    password: str

class PasswordResetConfirmResponseSchema(BaseResponseSchema):
    """
    Схема ответа на установку нового пароля.
    
    Отправляется пользователю после успешного изменения пароля.
    
    Attributes:
        success: Признак успешной смены пароля.
        message: Информационное сообщение о результате операции.
    """
    success: bool = True
    message: str = "Пароль успешно изменен"