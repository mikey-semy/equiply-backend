from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.modules.kanban import KanbanCardModel
    from app.models.v1.modules.lists import ListItemModel
    from app.models.v1.modules.posts import PostModel
    from app.models.v1.modules.tables import TableRowModel
    from app.models.v1.workspaces import WorkspaceModel


class IntegrationType(str, Enum):
    """Типы интеграций между модулями"""

    KANBAN_TO_BLOG = "kanban_to_blog"  # Канбан -> Блог
    TABLE_TO_BLOG = "table_to_blog"  # Таблица -> Блог
    LIST_TO_BLOG = "list_to_blog"  # Список -> Блог
    KANBAN_TO_LIST = "kanban_to_list"  # Канбан -> Список
    TABLE_TO_KANBAN = "table_to_kanban"  # Таблица -> Канбан


class ModuleIntegrationModel(BaseModel):
    """
    Модель интеграции между модулями

    Attributes:
        name (str): Название интеграции
        description (str): Описание интеграции
        integration_type (IntegrationType): Тип интеграции
        is_active (bool): Активна ли интеграция
        settings (Dict[str, Any]): Настройки интеграции
        workspace_id (int): ID рабочего пространства
        workspace (WorkspaceModel): Связь с моделью рабочего пространства
    """

    __tablename__ = "module_integrations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    integration_type: Mapped[IntegrationType] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    workspace: Mapped["WorkspaceModel"] = relationship(
        "WorkspaceModel", back_populates="module_integrations"
    )

    linked_items: Mapped[list["LinkedItemModel"]] = relationship(
        "LinkedItemModel", back_populates="integration", cascade="all, delete-orphan"
    )


class LinkedItemModel(BaseModel):
    """
    Модель связанных элементов между модулями

    Эта модель связывает элементы из разных модулей (канбан, блог, таблицы, списки)

    Attributes:
        integration_id (int): ID интеграции
        post_id (int): ID поста в блоге (опционально)
        kanban_card_id (int): ID карточки канбана (опционально)
        table_row_id (int): ID строки таблицы (опционально)
        list_item_id (int): ID элемента списка (опционально)
        metadata (Dict[str, Any]): Метаданные связи
    """

    __tablename__ = "linked_items"

    integration_id: Mapped[int] = mapped_column(
        ForeignKey("module_integrations.id", ondelete="CASCADE"), nullable=False
    )

    # Опциональные связи с разными типами элементов
    post_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("posts.id", ondelete="SET NULL"), nullable=True
    )
    kanban_card_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("kanban_cards.id", ondelete="SET NULL"), nullable=True
    )
    table_row_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("table_rows.id", ondelete="SET NULL"), nullable=True
    )
    list_item_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("list_items.id", ondelete="SET NULL"), nullable=True
    )

    link_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    # Связи
    integration: Mapped["ModuleIntegrationModel"] = relationship(
        "ModuleIntegrationModel", back_populates="linked_items"
    )
    post: Mapped[Optional["PostModel"]] = relationship("PostModel")
    kanban_card: Mapped[Optional["KanbanCardModel"]] = relationship("KanbanCardModel")
    table_row: Mapped[Optional["TableRowModel"]] = relationship("TableRowModel")
    list_item: Mapped[Optional["ListItemModel"]] = relationship("ListItemModel")
