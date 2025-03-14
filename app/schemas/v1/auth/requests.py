"""
Схемы для аутентификации и управления пользователями.
"""

from pydantic import Field, EmailStr

from app.schemas.v1.base import BaseRequestSchema


class AuthSchema(BaseRequestSchema):
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

class ForgotPasswordSchema(BaseRequestSchema):
    """
    Схема для запроса сброса пароля.

    Используется когда пользователь забыл пароль и хочет его восстановить.

    Attributes:
        email: Электронная почта пользователя, на которую будет отправлена инструкция по сбросу пароля.
    """
    email: EmailStr

class PasswordResetConfirmSchema(BaseRequestSchema):
    """
    Схема для установки нового пароля.

    Используется после подтверждения запроса на сброс пароля для установки нового пароля пользователя.

    Attributes:
        password: Новый пароль пользователя, который заменит предыдущий.
    """
    password: str