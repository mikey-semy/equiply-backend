"""
Модуль схем пользователя.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.v1.register.schema import RegistrationSchema

from ..base import (BaseInputSchema, BaseResponseSchema, BaseSchema,
                    ListResponseSchema)


class UserRole(str, Enum):
    """
    Роли пользователя в системе.

    Attributes:
        ADMIN (str): Роль администратора.
        MODERATOR (str): Роль модератора.
        USER (str): Роль пользователя.
        MANAGER (str): Роль менеджера.
    """

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    MANAGER = "manager"


class UserSchema(BaseSchema):
    """
    Схема пользователя.

    Attributes:
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        middle_name (str): Отчество пользователя.
        role (UserRole): Роль пользователя.
        email (EmailStr): Email пользователя.
        phone (str): Телефон пользователя.
        avatar (str): Ссылка на аватар пользователя.
        is_active (bool): Флаг активности пользователя.
        is_online (bool): Флаг онлайн-статуса пользователя.
        last_seen (datetime): Дата и время последнего визита пользователя.
    """

    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    role: UserRole
    email: EmailStr
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True
    is_online: bool = False
    last_seen: Optional[datetime] = None


class UserCredentialsSchema(BaseInputSchema):
    """
    Схема учетных данных пользователя.


    Attributes:
        id (int): Идентификатор пользователя.
        name (str): Имя пользователя (необязательно).
        email (str): Email пользователя.
        hashed_password (str | None): Хешированный пароль пользователя.
        is_active (bool): Флаг активности пользователя.
    """

    id: int | None = None
    name: str | None = None
    email: str
    hashed_password: str | None = None
    is_active: bool = True


class UserCreateSchema(RegistrationSchema):
    """
    Схема создания пользователя.

    см. в RegistrationSchema
    """


class UserUpdateSchema(BaseInputSchema):
    """
    Схема обновления данных пользователя

    Attributes:
        first_name (str | None): Имя пользователя.
        last_name (str | None): Фамилия пользователя.
        middle_name (str | None): Отчество пользователя.
        phone (str | None): Телефон пользователя.
    """

    first_name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=2, max_length=50)
    middle_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )

    class Config:
        extra = "forbid"


class UserResponseSchema(BaseResponseSchema):
    """
    Схема ответа пользователя.

    Attributes:
        id (int): Идентификатор пользователя.
        name (str): Имя пользователя.
        email (str): Email пользователя.
        role (UserRole): Роль пользователя.
    """

    id: int
    name: str
    email: str
    role: UserRole
    success: bool = True
    message: str = "Пользовател успешно получен."


class UserStatusResponseSchema(BaseResponseSchema):
    """
    Схема ответа статуса пользователя.

    Attributes:
        success (bool): Успешность запроса
        message (str): Сообщение о результате
        is_online (bool): Онлайн ли пользователь
        last_activity (Optional[int]): Время последней активности в Unix timestamp
    """

    success: bool = True
    message: str = "Статус пользователя успешно получен"
    is_online: bool
    last_activity: Optional[int] = None


class UserStatusesListResponseSchema(ListResponseSchema[UserStatusResponseSchema]):
    """
    Схема ответа со списком статусов пользователей
    """

    success: bool = True
    message: str = "Статусы пользователей успешно получены"
