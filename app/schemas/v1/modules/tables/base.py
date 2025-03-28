"""
Базовые схемы для модуля таблиц.
"""

from typing import Any, Dict, List, Optional

from app.schemas.v1.base import BaseSchema


class TableColumnSchema(BaseSchema):
    """
    Схема столбца таблицы.

    Attributes:
        name (str): Название столбца
        type (str): Тип данных столбца (string, number, boolean, date, etc.)
        required (bool): Обязательное ли поле
        default (Any): Значение по умолчанию
        options (Dict[str, Any]): Дополнительные опции столбца
    """

    name: str
    type: str
    required: bool = False
    default: Any = None
    options: Dict[str, Any] = {}


class TableSchema(BaseSchema):
    """
    Схема структуры таблицы.

    Attributes:
        columns (List[TableColumnSchema]): Список столбцов таблицы
        options (Dict[str, Any]): Дополнительные опции схемы
    """

    columns: List[TableColumnSchema]
    options: Dict[str, Any] = {}


class TableDefinitionDataSchema(BaseSchema):
    """
    Схема данных определения таблицы.

    Attributes:
        name (str): Название таблицы
        description (Optional[str]): Описание таблицы
        table_schema (Dict[str, Any]): Схема таблицы
        display_settings (Dict[str, Any]): Настройки отображения
        workspace_id (int): ID рабочего пространства
    """

    name: str
    description: Optional[str] = None
    table_schema: Dict[str, Any]
    display_settings: Dict[str, Any] = {}
    workspace_id: int


class TableRowDataSchema(BaseSchema):
    """
    Схема данных строки таблицы.

    Attributes:
        table_definition_id (int): ID определения таблицы
        data (Dict[str, Any]): Данные строки
    """

    table_definition_id: int
    data: Dict[str, Any]
