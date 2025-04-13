from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.modules.templates import ModuleTemplateModel
    from app.models.v1.workspaces import WorkspaceModel


class KanbanBoardSettingsModel(BaseModel):
    __tablename__ = "kanban_board_settings"

    board_id: Mapped[int] = mapped_column(
        ForeignKey("kanban_boards.id", ondelete="CASCADE"), primary_key=True
    )
    display_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    automation_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    notification_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    access_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    board: Mapped["KanbanBoardModel"] = relationship(
        "KanbanBoardModel", back_populates="settings"
    )


class KanbanBoardModel(BaseModel):
    """
    Модель канбан-доски

    Attributes:
        name (str): Название канбан-доски
        description (str): Описание канбан-доски
        columns (List[KanbanColumnModel]): Связь с моделями колонок канбан-доски
        display_settings (Dict[str, Any]): Настройки отображения доски
        workspace_id (int): ID рабочего пространства
        workspace (WorkspaceModel): Связь с моделью рабочего пространства
    """

    __tablename__ = "kanban_boards"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    settings: Mapped["KanbanBoardSettingsModel"] = relationship(
        "KanbanBoardSettingsModel",
        back_populates="board",
        uselist=False,
        cascade="all, delete-orphan",
    )
    columns: Mapped[List["KanbanColumnModel"]] = relationship(
        "KanbanColumnModel", back_populates="board", cascade="all, delete-orphan"
    )

    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    workspace: Mapped["WorkspaceModel"] = relationship(
        "WorkspaceModel", back_populates="kanban_boards"
    )
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("module_templates.id", ondelete="SET NULL"), nullable=True
    )

    template: Mapped[Optional["ModuleTemplateModel"]] = relationship(
        "ModuleTemplateModel", back_populates="kanban_boards"
    )


class KanbanColumnModel(BaseModel):
    """
    Модель колонки канбан-доски

    Attributes:
        name (str): Название колонки
        order (int): Порядок колонки на доске
        wip_limit (int): Лимит работы в процессе (Work In Progress)
        cards (List[KanbanCardModel]): Связь с моделями карточек в колонке
        board_id (int): ID канбан-доски
        board (KanbanBoardModel): Связь с моделью канбан-доски
    """

    __tablename__ = "kanban_columns"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    wip_limit: Mapped[Optional[int]] = mapped_column(Integer)

    cards: Mapped[List["KanbanCardModel"]] = relationship(
        "KanbanCardModel", back_populates="column", cascade="all, delete-orphan"
    )

    board_id: Mapped[int] = mapped_column(
        ForeignKey("kanban_boards.id", ondelete="CASCADE"), nullable=False
    )
    board: Mapped["KanbanBoardModel"] = relationship(
        "KanbanBoardModel", back_populates="columns"
    )


class KanbanCardModel(BaseModel):
    """
    Модель карточки канбан-доски

    Attributes:
        title (str): Заголовок карточки
        description (str): Описание карточки
        order (int): Порядок карточки в колонке
        data (Dict[str, Any]): Дополнительные данные карточки (метки, приоритет и т.д.)
        column_id (int): ID колонки
        column (KanbanColumnModel): Связь с моделью колонки
    """

    __tablename__ = "kanban_cards"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    column_id: Mapped[int] = mapped_column(
        ForeignKey("kanban_columns.id", ondelete="CASCADE"), nullable=False
    )
    column: Mapped["KanbanColumnModel"] = relationship(
        "KanbanColumnModel", back_populates="cards"
    )
