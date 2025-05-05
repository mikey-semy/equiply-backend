"""
Модуль схем групп пользователей.
"""

from typing import Optional

from pydantic import Field

from app.schemas.v1.base import BaseSchema


class UserGroupSchema(BaseSchema):
    """
    Схема группы пользователей.

    Attributes:
        name (str): Название группы пользователей.
        description (Optional[str]): Описание группы пользователей.
        is_active (bool): Флаг активности группы.
        workspace_id (Optional[int]): ID рабочего пространства, к которому относится группа.
    """
    name: str = Field(..., description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")
    is_active: bool = Field(True, description="Активна ли группа")
    workspace_id: Optional[int] = Field(None, description="ID рабочего пространства")


class UserGroupMemberSchema(BaseSchema):
    """
    Схема для члена группы.

    Attributes:
        group_id (int): ID группы, к которой относится пользователь.
        user_id (int): ID пользователя, который является членом группы.
    """
    group_id: int = Field(..., description="ID группы")
    user_id: int = Field(..., description="ID пользователя")
