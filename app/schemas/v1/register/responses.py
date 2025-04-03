"""
Схемы для регистрации пользователей.
"""

from pydantic import EmailStr

from app.schemas.v1.base import BaseResponseSchema


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


class ResendVerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа на запрос повторной отправки письма верификации

    Attributes:
        email (EmailStr): Email пользователя
        message (str): Сообщение о результате операции
    """

    email: EmailStr
    message: str = "Письмо для подтверждения email отправлено"


class VerificationStatusResponseSchema(BaseResponseSchema):
    """
    Схема ответа о статусе верификации email

    Attributes:
        email (EmailStr): Email пользователя
        is_verified (bool): Статус верификации
        message (str): Сообщение о статусе верификации
    """

    email: EmailStr
    is_verified: bool
    message: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        self.message = (
            "Email подтвержден" if self.is_verified else "Email не подтвержден"
        )
