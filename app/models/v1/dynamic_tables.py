from typing import List, Dict, Any, Optional
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.v1.base import BaseModel
from app.models.v1 import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.v1.workspaces import WorkspaceModel

class TableDefinitionModel(BaseModel):
    """
    Модель определения таблицы

    Attributes:
        name (str): Название таблицы
        description (str): Описание таблицы
        schema (Dict[str, Any]): Схема таблицы (например, столбцы и их типы)
        table_rows (List[TableRowModel]): Связь с моделями строк таблицы

        display_settings (Dict[str, Any]): Настройки отображения таблицы (например, порядок столбцов)


    """

    __tablename__ = "table_definitions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    schema: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    table_rows: Mapped[List["TableRowModel"]] = relationship("TableRowModel", back_populates="table_definition", cascade="all, delete-orphan")

    # Метаданные для отображения таблицы (порядок столбцов и пр.)
    display_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    workspace: Mapped["WorkspaceModel"] = relationship("WorkspaceModel", back_populates="tables")

class TableRowModel(BaseModel):
    """
    Модель строки в динамической таблице

    Attributes:
        table_definition_id (int): Идентификатор таблицы, к которой относится эта строка.
        data (Dict[str, Any]): Данные строки в виде словаря.

    Relationships:
        table_definition (TableDefinitionModel): Связь с моделью таблицы, к которой относится эта строка.
    """

    __tablename__ = "table_rows"

    table_definition_id: Mapped[int] = mapped_column(ForeignKey("table_definitions.id", ondelete="CASCADE"), nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    table_definition: Mapped["TableDefinitionModel"] = relationship("TableDefinitionModel", back_populates="table_rows")