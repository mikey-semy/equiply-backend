"""
Схемы запросов для модуля таблиц.
"""

from typing import Any, Dict, Optional

from pydantic import Field, field_validator

from app.schemas.v1.base import BaseRequestSchema


class CreateTableSchema(BaseRequestSchema):
    """
    Схема создания таблицы.

    Attributes:
        workspace_id (int): ID рабочего пространства
        name (str): Название таблицы
        description (Optional[str]): Описание таблицы
        table_schema (Dict[str, Any]): Схема таблицы
        display_settings (Dict[str, Any]): Настройки отображения
    """

    workspace_id: int = Field(..., description="ID рабочего пространства")
    name: str = Field(..., min_length=1, max_length=255, description="Название таблицы")
    description: Optional[str] = Field(
        None, max_length=500, description="Описание таблицы"
    )
    table_schema: Dict[str, Any] = Field(..., description="Схема таблицы (столбцы и их типы)")
    display_settings: Dict[str, Any] = Field(
        {}, description="Настройки отображения таблицы"
    )

    @field_validator("table_schema")
    def validate_schema(cls, v):
        # Базовая валидация схемы
        if not isinstance(v, dict):
            raise ValueError("Схема должна быть объектом")

        if "columns" not in v:
            raise ValueError("Схема должна содержать поле 'columns'")

        if not isinstance(v["columns"], list):
            raise ValueError("Поле 'columns' должно быть массивом")

        for column in v["columns"]:
            if not isinstance(column, dict):
                raise ValueError("Каждый столбец должен быть объектом")

            if "name" not in column:
                raise ValueError("Каждый столбец должен иметь поле 'name'")

            if "type" not in column:
                raise ValueError("Каждый столбец должен иметь поле 'type'")

        return v


class UpdateTableSchema(BaseRequestSchema):
    """
    Схема обновления таблицы.

    Attributes:
        name (Optional[str]): Новое название таблицы
        description (Optional[str]): Новое описание таблицы
        table_schema (Optional[Dict[str, Any]]): Новая схема таблицы
        display_settings (Optional[Dict[str, Any]]): Новые настройки отображения
    """

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Новое название таблицы"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Новое описание таблицы"
    )
    table_schema: Optional[Dict[str, Any]] = Field(None, description="Новая схема таблицы")
    display_settings: Optional[Dict[str, Any]] = Field(
        None, description="Новые настройки отображения"
    )

    @field_validator("table_schema")
    def validate_schema(cls, v):
        if v is None:
            return v

        # Базовая валидация схемы
        if not isinstance(v, dict):
            raise ValueError("Схема должна быть объектом")

        if "columns" not in v:
            raise ValueError("Схема должна содержать поле 'columns'")

        if not isinstance(v["columns"], list):
            raise ValueError("Поле 'columns' должно быть массивом")

        for column in v["columns"]:
            if not isinstance(column, dict):
                raise ValueError("Каждый столбец должен быть объектом")

            if "name" not in column:
                raise ValueError("Каждый столбец должен иметь поле 'name'")

            if "type" not in column:
                raise ValueError("Каждый столбец должен иметь поле 'type'")

        return v


class CreateTableRowSchema(BaseRequestSchema):
    """
    Схема создания строки таблицы.

    Attributes:
        data (Dict[str, Any]): Данные строки
    """

    data: Dict[str, Any] = Field(..., description="Данные строки таблицы")


class UpdateTableRowSchema(BaseRequestSchema):
    """
    Схема обновления строки таблицы.

    Attributes:
        data (Dict[str, Any]): Новые данные строки
    """

    data: Dict[str, Any] = Field(..., description="Новые данные строки таблицы")


class CreateTableFromTemplateSchema(BaseRequestSchema):
    """
    Схема создания таблицы из шаблона.

    Attributes:
        workspace_id (int): ID рабочего пространства
        template_id (int): ID шаблона
        name (Optional[str]): Название новой таблицы (если не указано, будет использовано название шаблона)
        description (Optional[str]): Описание новой таблицы (если не указано, будет использовано описание шаблона)
    """

    workspace_id: int = Field(..., description="ID рабочего пространства")
    template_id: int = Field(..., description="ID шаблона")
    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название новой таблицы"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Описание новой таблицы"
    )
