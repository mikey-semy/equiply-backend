import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.modules.kanban import KanbanBoardModel
    from app.models.v1.modules.lists import ListDefinitionModel
    from app.models.v1.modules.posts import PostModel
    from app.models.v1.modules.tables import TableDefinitionModel
    from app.models.v1.users import UserModel


class ModuleType(str, Enum):
    """Типы модулей для шаблонов"""

    TABLE = "table"
    LIST = "list"
    KANBAN = "kanban"
    BLOG = "blog"


class ModuleTemplateModel(BaseModel):
    """
    Модель шаблона модуля

    Attributes:
        name (str): Название шаблона
        description (str): Описание шаблона
        module_type (ModuleType): Тип модуля (table, list, kanban, blog)
        template_data (Dict[str, Any]): Данные шаблона
        is_public (bool): Доступен ли шаблон всем пользователям
        creator_id (UUID): ID создателя шаблона

    Relationships:
        creator (UserModel): Создатель шаблона
        tables (List[TableDefinitionModel]): Таблицы, созданные по этому шаблону
        lists (List[ListDefinitionModel]): Списки, созданные по этому шаблону
        kanban_boards (List[KanbanBoardModel]): Канбан-доски, созданные по этому шаблону
        posts (List[PostModel]): Посты, созданные по этому шаблону
    """

    __tablename__ = "module_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    module_type: Mapped[ModuleType] = mapped_column(nullable=False)
    template_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_public: Mapped[bool] = mapped_column(default=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Связи
    creator: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="created_templates"
    )

    # Связи с модулями, созданными по этому шаблону
    tables: Mapped[List["TableDefinitionModel"]] = relationship(
        "TableDefinitionModel", back_populates="template"
    )

    lists: Mapped[List["ListDefinitionModel"]] = relationship(
        "ListDefinitionModel", back_populates="template"
    )

    kanban_boards: Mapped[List["KanbanBoardModel"]] = relationship(
        "KanbanBoardModel", back_populates="template"
    )

    posts: Mapped[List["PostModel"]] = relationship(
        "PostModel", back_populates="template"
    )
