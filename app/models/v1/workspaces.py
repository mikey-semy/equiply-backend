from enum import Enum
from typing import List, Optional

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.modules.lists import ListDefinitionModel
    from app.models.v1.modules.tables import TableDefinitionModel
    from app.models.v1.users import UserModel


class WorkspaceRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    EDITOR = "editor"
    VIEWER = "viewer"


class WorkspaceModel(BaseModel):
    """
    Модель рабочего пространства

    Attributes:
        name (str): Название рабочего пространства
        description (str): Описание рабочего пространства
        owner_id (int): ID владельца
        is_public (bool): Флаг публичности

    Relationships:
        owner (UserModel): Владелец рабочего пространства
        members (List[WorkspaceMemberModel]): Участники рабочего пространства
        tables (List[TableDefinitionModel]): Таблицы рабочего пространства
        lists (List[ListDefinitionModel]): Списки рабочего пространства
    """

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_public: Mapped[bool] = mapped_column(default=False)

    # Связи
    owner: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[owner_id], back_populates="owned_workspaces"
    )
    members: Mapped[List["WorkspaceMemberModel"]] = relationship(
        "WorkspaceMemberModel", back_populates="workspace", cascade="all, delete-orphan"
    )
    tables: Mapped[List["TableDefinitionModel"]] = relationship(
        "TableDefinitionModel", back_populates="workspace", cascade="all, delete-orphan"
    )
    lists: Mapped[List["ListDefinitionModel"]] = relationship(
        "ListDefinitionModel", back_populates="workspace", cascade="all, delete-orphan"
    )


class WorkspaceMemberModel(BaseModel):
    """
    Модель участника рабочего пространства

    Attributes:
        workspace_id (int): ID рабочего пространства
        user_id (int): ID пользователя
        role (WorkspaceRole): Роль пользователя в рабочем пространстве

    Relationships:
        workspace (WorkspaceModel): Рабочее пространство
        user (UserModel): Пользователь
    """

    __tablename__ = "workspace_members"

    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[WorkspaceRole] = mapped_column(
        SQLEnum(WorkspaceRole), default=WorkspaceRole.VIEWER
    )

    # Связи
    workspace: Mapped["WorkspaceModel"] = relationship(
        "WorkspaceModel", back_populates="members"
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="workspace_memberships"
    )
