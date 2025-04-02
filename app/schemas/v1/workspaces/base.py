"""
Базовые схемы для модуля рабочих пространств.
"""

from typing import List, Optional

from app.models.v1.workspaces import WorkspaceRole
from app.schemas.v1.base import BaseSchema, CommonBaseSchema


class WorkspaceMemberDataSchema(CommonBaseSchema):
    """
    Схема данных участника рабочего пространства.

    Attributes:
        user_id (int): ID пользователя
        workspace_id (int): ID рабочего пространства
        role (WorkspaceRole): Роль пользователя в рабочем пространстве
        username (str): Имя пользователя
        email (str): Email пользователя
    """

    user_id: int
    workspace_id: int
    role: WorkspaceRole
    username: str
    email: str


class WorkspaceDataSchema(BaseSchema):
    """
    Схема данных рабочего пространства.

    Attributes:
        name (str): Название рабочего пространства
        description (Optional[str]): Описание рабочего пространства
        owner_id (int): ID владельца
        is_public (bool): Флаг публичности
    """

    name: str
    description: Optional[str] = None
    owner_id: int
    is_public: bool = False


class WorkspaceDetailDataSchema(WorkspaceDataSchema):
    """
    Схема детальных данных рабочего пространства.

    Attributes:
        members (List[WorkspaceMemberDataSchema]): Участники рабочего пространства
        tables_count (int): Количество таблиц в рабочем пространстве
        lists_count (int): Количество списков в рабочем пространстве
        kanban_boards_count (int): Количество канбан-досок в рабочем пространстве
        posts_count (int): Количество постов в рабочем пространстве
    """

    members: List[WorkspaceMemberDataSchema] = []
    tables_count: int = 0
    lists_count: int = 0
    kanban_boards_count: int = 0
    posts_count: int = 0
