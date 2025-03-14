"""
Схемы для регистрации пользователей.
"""

from pydantic import EmailStr
from app.schemas.v1.base import  BaseResponseSchema


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
        message (str): Сообщение об успешной верификации
    """
    user_id: int
    message: str = "Email успешно подтвержден"
