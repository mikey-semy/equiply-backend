"""
Модуль схем пользователя.
"""
from pydantic import EmailStr, Field

from app.models.v1.users import UserRole
from app.schemas.v1.base import BaseRequestSchema

class UserCredentialsSchema(BaseRequestSchema):
    """
    Схема данных пользователя для аутентификации.

    Attributes:
        id (int): ID пользователя
        username (str): Имя пользователя (логин)
        email (EmailStr): Email пользователя
        role (UserRole): Роль пользователя
        hashed_password (str): Хешированный пароль
        is_active (bool): Активен ли пользователь
        is_verified (bool): Подтвержден ли email
    """
    id: int
    username: str
    email: EmailStr
    role: UserRole
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False

class UserUpdateSchema(BaseRequestSchema):
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

class ToggleUserActiveSchema(BaseRequestSchema):
    """
    Схема для изменения статуса активности пользователя.

    Attributes:
        user_id (int): Идентификатор пользователя.
        is_active (bool): Новый статус активности пользователя (true - активен, false - заблокирован).
    """
    user_id: int = Field(..., description="Идентификатор пользователя")
    is_active: bool = Field(..., description="Статус активности пользователя (true - активен, false - заблокирован)")


class AssignUserRoleSchema(BaseRequestSchema):
    """
    Схема для назначения роли пользователю.

    Attributes:
        user_id (int): Идентификатор пользователя.
        role (UserRole): Новая роль пользователя.
    """
    user_id: int = Field(..., description="Идентификатор пользователя")
    role: UserRole = Field(..., description="Новая роль пользователя")