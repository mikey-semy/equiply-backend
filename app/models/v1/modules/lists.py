from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.modules.templates import ModuleTemplateModel
    from app.models.v1.workspaces import WorkspaceModel


class ListDefinitionModel(BaseModel):
    """
    Модель определения списка

    Attributes:
        name (str): Название списка
        description (str): Описание списка
        workspace_id (int): ID проекта
        schema (Dict[str, Any]): Схема элементов списка
        display_settings (Dict[str, Any]): Настройки отображения

    Relationships:
        workspace (ProjectModel): Проект
        items (List[ListItemModel]): Элементы списка
    """

    __tablename__ = "list_definitions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    schema: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    display_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("module_templates.id", ondelete="SET NULL"), nullable=True
    )

    template: Mapped[Optional["ModuleTemplateModel"]] = relationship(
        "ModuleTemplateModel", back_populates="lists"
    )
    workspace: Mapped["WorkspaceModel"] = relationship(
        "WorkspaceModel", back_populates="lists"
    )
    items: Mapped[List["ListItemModel"]] = relationship(
        "ListItemModel", back_populates="list_definition", cascade="all, delete-orphan"
    )


class ListItemModel(BaseModel):
    """
    Модель элемента списка

    Attributes:
        list_definition_id (int): ID списка
        data (Dict[str, Any]): Данные элемента
        is_completed (bool): Флаг завершения (для задач)

    Relationships:
        list_definition (ListDefinitionModel): Определение списка
    """

    __tablename__ = "list_items"

    list_definition_id: Mapped[int] = mapped_column(
        ForeignKey("list_definitions.id", ondelete="CASCADE"), nullable=False
    )
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_completed: Mapped[bool] = mapped_column(
        default=False
    )  # Полезно для списков задач

    # Связи
    list_definition: Mapped["ListDefinitionModel"] = relationship(
        "ListDefinitionModel", back_populates="items"
    )
