"""
Модуль схем пользователя.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.v1.register.register import RegistrationSchema

from ..base import (BaseInputSchema, BaseResponseSchema, BaseSchema,
                    ListResponseSchema)


class UserRole(str, Enum):
    """
    Роли пользователя в системе.

    Attributes:
        ADMIN (str): Роль администратора.
        MODERATOR (str): Роль модератора.
        USER (str): Роль пользователя.
    """

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class UserSchema(BaseSchema):
    """
    Схема пользователя.

    Attributes:
        username (str): Имя пользователя.
        role (UserRole): Роль пользователя.
        email (EmailStr): Email пользователя.
        phone (str): Телефон пользователя.
        avatar (str): Ссылка на аватар пользователя.
        is_active (bool): Флаг активности пользователя.
        is_verified (bool): Подтвержден ли email
        is_online (bool): Флаг онлайн-статуса пользователя.
        last_seen (datetime): Дата и время последнего визита пользователя.
    """

    username: str
    role: UserRole
    email: EmailStr
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_online: bool = False
    last_seen: Optional[datetime] = None


class UserCredentialsSchema(BaseInputSchema):
    """
    Схема данных пользователя для аутентификации.
    
    Attributes:
        id (int): ID пользователя
        username (str): Имя пользователя (логин)
        email (EmailStr): Email пользователя
        hashed_password (str): Хешированный пароль
        is_active (bool): Активен ли пользователь
        is_verified (bool): Подтвержден ли email
    """
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False


class UserCreateSchema(RegistrationSchema):
    """
    Схема создания пользователя.

    см. в RegistrationSchema
    """


class UserUpdateSchema(BaseInputSchema):
    """
    Схема обновления данных пользователя

    Attributes:
        username (str | None): Имя пользователя.
        phone (str | None): Телефон пользователя.
    """

    username: str | None = Field(None, min_length=2, max_length=50)
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
        username (str): Имя пользователя.
        email (str): Email пользователя.
        role (UserRole): Роль пользователя.
    """

    id: int
    username: str
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
