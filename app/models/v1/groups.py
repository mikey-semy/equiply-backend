from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.users import UserModel
    from app.models.v1.workspaces import WorkspaceModel

class UserGroupModel(BaseModel):
    """
    Модель группы пользователей.

    Attributes:
        name (str): Название группы
        description (str): Описание группы
        is_active (bool): Активна ли группа
        workspace_id (int): ID рабочего пространства, к которому относится группа
    """
    __tablename__ = "user_groups"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    workspace_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workspaces.id"), nullable=True
    )

    # Отношения
    members: Mapped[List["UserGroupMemberModel"]] = relationship(
        "UserGroupMemberModel", back_populates="group", cascade="all, delete-orphan"
    )
    workspace: Mapped["WorkspaceModel"] = relationship(
        "WorkspaceModel", back_populates="user_groups"
    )


class UserGroupMemberModel(BaseModel):
    """
    Модель для связи пользователей с группами.

    Attributes:
        group_id (int): ID группы
        user_id (int): ID пользователя
    """
    __tablename__ = "user_group_members"

    group_id: Mapped[int] = mapped_column(
        ForeignKey("user_groups.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    # Отношения
    group: Mapped["UserGroupModel"] = relationship(
        "UserGroupModel", back_populates="members"
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="group_memberships"
    )
