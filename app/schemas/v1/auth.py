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
        description="Пароль (минимум 8 символов, заглавная и строчная буква, цифра, спецсимвол",
    )

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
        message: Сообщение об успешной авторизации
    """
    access_token: str
    token_type: str = settings.TOKEN_TYPE
    message: str = "Авторизация успешна"

class LogoutResponseSchema(BaseResponseSchema):
    """
    Схема ответа для выхода из системы.
    
    Отправляется клиенту после успешного завершения сессии и выхода пользователя из системы.
    
    Attributes:
        message: Информационное сообщение о результате операции.
    """
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
        message: Информационное сообщение о результате операции и дальнейших действиях.
    """
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
        message: Информационное сообщение о результате операции.
    """
    message: str = "Пароль успешно изменен"