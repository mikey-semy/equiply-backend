import uuid
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.v1.base import BaseModel
from app.models.v1 import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.v1.users import UserModel
    from app.models.v1.workspaces import WorkspaceModel


class BrigadeModel(BaseModel):
    """
    Модель бригады для быстрого выбора участников
    """
    __tablename__ = "brigades"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    subdivision: Mapped[str] = mapped_column(nullable=False)  # подразделение бригады
    is_active: Mapped[bool] = mapped_column(default=True)

    # Связь с рабочим пространством (опционально)
    workspace_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workspaces.id"), nullable=True
    )

    # Отношения
    members: Mapped[List["BrigadeMemberModel"]] = relationship(
        "BrigadeMemberModel", back_populates="brigade", cascade="all, delete-orphan"
    )
    workspace: Mapped[Optional["WorkspaceModel"]] = relationship("WorkspaceModel")


class BrigadeMemberModel(BaseModel):
    """
    Модель члена бригады (для каталога/быстрого выбора)
    """
    __tablename__ = "brigade_members"

    brigade_id: Mapped[int] = mapped_column(ForeignKey("brigades.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Отношения
    brigade: Mapped["BrigadeModel"] = relationship(
        "BrigadeModel", back_populates="members"
    )
    user: Mapped["UserModel"] = relationship("UserModel")
