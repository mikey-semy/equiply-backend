"""
Модуль схем пользователя.
"""
from app.schemas.v1.base import BaseResponseSchema
from .base import UserDetailSchema, UserStatusData

class UserResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными пользователя.

    Attributes:
        message (str): Сообщение о результате операции.
        data (UserDetailSchema): Данные пользователя.
    """
    message: str = "Пользователь успешно получен."
    data: UserDetailSchema

class UserStatusResponseSchema(BaseResponseSchema):
    """
    Схема ответа статуса пользователя.

    Attributes:
        message (str): Сообщение о результате
        data (UserStatusData): Информация о статусе пользователя
    """
    message: str = "Статус пользователя успешно получен"
    data: UserStatusData
