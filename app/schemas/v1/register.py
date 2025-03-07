"""
Схемы для регистрации пользователей.
"""

from pydantic import EmailStr, Field

from .base import BaseInputSchema, BaseResponseSchema


class RegistrationSchema(BaseInputSchema):
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
    password: str = Field(min_length=8, description="Пароль минимум 8 символов")


class RegistrationResponseSchema(BaseResponseSchema):
    """
    Схема ответа при успешной регистрации

    Attributes:
        user_id (int): ID пользователя
        email (str): Email пользователя
        message (str): Сообщение об успешной регистрации
    """

    user_id: int
    email: EmailStr
    message: str = "Регистрация успешно завершена"

class VerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа при успешной верификации email

    Attributes:
        user_id (int): ID пользователя
        success (bool): Успешно ли подтвержден email
        message (str): Сообщение об успешной верификации
    """
    user_id: int
    success: bool = True
    message: str = "Email успешно подтвержден"
