"""
Модуль схем пользователя.
"""

from app.schemas.v1.base import BaseResponseSchema

from .base import UserDetailDataSchema, UserStatusDataSchema


class UserResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными пользователя.

    Attributes:
        message (str): Сообщение о результате операции.
        data (UserDetailDataSchema): Данные пользователя.
    """

    message: str = "Пользователь успешно получен."
    data: UserDetailDataSchema


class UserStatusResponseSchema(BaseResponseSchema):
    """
    Схема ответа статуса пользователя.

    Attributes:
        message (str): Сообщение о результате
        data (UserStatusDataSchema): Информация о статусе пользователя
    """

    message: str = "Статус пользователя успешно получен"
    data: UserStatusDataSchema


class UserUpdateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при обновлении данных пользователя.

    Attributes:
        message (str): Сообщение о результате операции.
        data (UserDetailDataSchema): Обновленные данные пользователя.
    """

    message: str = "Данные пользователя успешно обновлены"
    data: UserDetailDataSchema


class UserRoleUpdateResponseSchema(UserUpdateResponseSchema):
    """
    Схема ответа при обновлении роли пользователя.

    Attributes:
        message (str): Сообщение о результате операции.
        data (UserDetailDataSchema): Обновленные данные пользователя.
    """

    message: str = "Роль пользователя успешно обновлена"


class UserActiveUpdateResponseSchema(UserUpdateResponseSchema):
    """
    Схема ответа при обновлении статуса активности пользователя.

    Attributes:
        message (str): Сообщение о результате операции.
        data (UserDetailDataSchema): Обновленные данные пользователя.
    """

    message: str = "Статус активности пользователя успешно обновлен"


class UserDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении пользователя.

    Attributes:
        message (str): Сообщение о результате операции.
    """

    message: str = "Пользователь успешно удален"
