"""
Схемы для регистрации пользователей.
"""

from pydantic import EmailStr, Field, field_validator

from app.core.security.password import BasePasswordValidator
from app.schemas.v1.base import BaseRequestSchema


class RegistrationSchema(BaseRequestSchema):
    """
    Схема создания нового пользователя.

    Attributes:
        username (str): Имя пользователя.
        email (str): Email пользователя.
        phone (str): Телефон пользователя.
        password (str): Пароль пользователя.
    """

    username: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(description="Email пользователя")
    phone: str | None = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
    password: str = Field(
        description="Пароль (минимум 8 символов, заглавная и строчная буква, цифра, спецсимвол)"
    )

    @field_validator("password")
    def validate_password(cls, v, info):
        data = info.data
        username = data.get("username", None)
        return BasePasswordValidator.validate_password_strength(v, username)


class ResendVerificationRequestSchema(BaseRequestSchema):
    """
    Схема запроса на повторную отправку письма верификации

    Attributes:
        email (EmailStr): Email пользователя
    """

    email: EmailStr = Field(description="Email пользователя")
