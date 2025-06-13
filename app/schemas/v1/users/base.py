"""
Модуль схем пользователя.
"""
import uuid
from typing import Optional

from pydantic import EmailStr

from app.models.v1.users import UserRole
from app.schemas.v1.base import CommonBaseSchema, UserBaseSchema


class UserSchema(UserBaseSchema):
    """
    Схема пользователя.

    Attributes:
        id (UUID): Идентификатор пользователя.
        username (str): Имя пользователя.
        role (UserRole): Роль пользователя.
        email (EmailStr): Email пользователя.
        phone (str): Телефон пользователя.
        avatar (str): Ссылка на аватар пользователя.
        is_active (bool): Флаг активности пользователя.
        is_verified (bool): Подтвержден ли email
        is_online (bool): Онлайн ли пользователь
    """

    username: str
    role: UserRole
    email: EmailStr
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_online: bool = False


class CurrentUserSchema(CommonBaseSchema):
    """
    Схема текущего аутентифицированного пользователя без чувствительных данных.

    Attributes:
        id (UUID): ID пользователя
        username (str): Имя пользователя (логин)
        email (EmailStr): Email пользователя
        role (UserRole): Роль пользователя
        is_active (bool): Активен ли пользователь
        is_verified (bool): Подтвержден ли email
    """

    id: uuid.UUID
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool = True
    is_verified: bool = False


class UserDetailDataSchema(UserBaseSchema):
    """
    Схема детальной информации о пользователе.

    Attributes:
        id (UUID): Идентификатор пользователя.
        username (str): Имя пользователя.
        email (str): Email пользователя.
        role (UserRole): Роль пользователя.
        is_active (bool): Активен ли пользователь.
    """

    username: str
    email: str
    role: UserRole
    is_active: bool = True


class UserStatusDataSchema(CommonBaseSchema):
    """
    Схема данных о статусе пользователя.

    Attributes:
        is_online (bool): Онлайн ли пользователь
        last_activity (Optional[int]): Время последней активности в Unix timestamp в секундах
    """

    is_online: bool
    last_activity: Optional[int] = None
