"""
Модуль схем запросов для групп пользователей.
"""
import uuid
from typing import Optional

from pydantic import Field

from app.schemas.v1.base import BaseRequestSchema


class UserGroupCreateRequestSchema(BaseRequestSchema):
    """
    Схема для создания группы пользователей.

    Attributes:
        name (str): Название группы пользователей.
        description (Optional[str]): Описание группы пользователей.
        workspace_id (Optional[int]): ID рабочего пространства, к которому относится группа.
    """
    name: str = Field(..., description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")
    workspace_id: Optional[int] = Field(None, description="ID рабочего пространства")


class UserGroupUpdateRequestSchema(BaseRequestSchema):
    """
    Схема для обновления группы пользователей.

    Attributes:
        name (Optional[str]): Новое название группы.
        description (Optional[str]): Новое описание группы.
        is_active (Optional[bool]): Новый статус активности группы.
    """
    name: Optional[str] = Field(None, description="Новое название группы")
    description: Optional[str] = Field(None, description="Новое описание группы")
    is_active: Optional[bool] = Field(None, description="Новый статус активности")


class AddUserToGroupRequestSchema(BaseRequestSchema):
    """
    Схема для добавления пользователя в группу.

    Attributes:
        user_id (uuid.UUID): ID пользователя, которого нужно добавить в группу.
    """
    user_id: uuid.UUID = Field(..., description="ID пользователя")


class RemoveUserFromGroupRequestSchema(BaseRequestSchema):
    """
    Схема для удаления пользователя из группы.

    Attributes:
        user_id (uuid.UUID): ID пользователя, которого нужно удалить из группы.
    """
    user_id: uuid.UUID = Field(..., description="ID пользователя")
