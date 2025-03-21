"""
Схемы запросов для модуля рабочих пространств.
"""

from typing import Optional

from pydantic import Field

from app.models.v1.workspaces import WorkspaceRole
from app.schemas.v1.base import BaseRequestSchema


class CreateWorkspaceSchema(BaseRequestSchema):
    """
    Схема создания рабочего пространства.

    Attributes:
        name (str): Название рабочего пространства
        description (Optional[str]): Описание рабочего пространства
        is_public (bool): Флаг публичности
    """

    name: str = Field(
        ..., min_length=1, max_length=255, description="Название рабочего пространства"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Описание рабочего пространства"
    )
    is_public: bool = Field(False, description="Флаг публичности рабочего пространства")


class UpdateWorkspaceSchema(BaseRequestSchema):
    """
    Схема обновления рабочего пространства.

    Attributes:
        name (Optional[str]): Новое название рабочего пространства
        description (Optional[str]): Новое описание рабочего пространства
        is_public (Optional[bool]): Новый флаг публичности
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Новое название рабочего пространства",
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Новое описание рабочего пространства"
    )
    is_public: Optional[bool] = Field(
        None, description="Новый флаг публичности рабочего пространства"
    )


class AddWorkspaceMemberSchema(BaseRequestSchema):
    """
    Схема добавления участника в рабочее пространство.

    Attributes:
        user_id (int): ID пользователя
        role (WorkspaceRole): Роль пользователя в рабочем пространстве
    """

    user_id: int = Field(..., description="ID пользователя")
    role: WorkspaceRole = Field(
        WorkspaceRole.VIEWER, description="Роль пользователя в рабочем пространстве"
    )


class UpdateWorkspaceMemberRoleSchema(BaseRequestSchema):
    """
    Схема обновления роли участника рабочего пространства.

    Attributes:
        user_id (int): ID пользователя
        role (WorkspaceRole): Новая роль пользователя в рабочем пространстве
    """

    user_id: int = Field(..., description="ID пользователя")
    role: WorkspaceRole = Field(
        ..., description="Новая роль пользователя в рабочем пространстве"
    )
