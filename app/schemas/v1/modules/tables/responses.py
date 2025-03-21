"""
Схемы ответов для модуля таблиц.
"""

from typing import List

from app.schemas.v1.base import BaseResponseSchema
from app.schemas.v1.modules.tables.base import (TableDefinitionDataSchema,
                                                TableRowDataSchema)


class TableDefinitionResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными определения таблицы.

    Attributes:
        message (str): Сообщение о результате операции
        data (TableDefinitionDataSchema): Данные определения таблицы
    """

    message: str = "Таблица успешно получена"
    data: TableDefinitionDataSchema


class TableDefinitionListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком определений таблиц.

    Attributes:
        message (str): Сообщение о результате операции
        data (List[TableDefinitionDataSchema]): Список данных определений таблиц
        total (int): Общее количество таблиц
    """

    message: str = "Список таблиц успешно получен"
    data: List[TableDefinitionDataSchema]
    total: int


class TableDefinitionCreateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при создании таблицы.

    Attributes:
        message (str): Сообщение о результате операции
        data (TableDefinitionDataSchema): Данные созданной таблицы
    """

    message: str = "Таблица успешно создана"
    data: TableDefinitionDataSchema


class TableDefinitionUpdateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при обновлении таблицы.

    Attributes:
        message (str): Сообщение о результате операции
        data (TableDefinitionDataSchema): Данные обновленной таблицы
    """

    message: str = "Таблица успешно обновлена"
    data: TableDefinitionDataSchema


class TableDefinitionDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении таблицы.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Таблица успешно удалена"


class TableRowResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными строки таблицы.

    Attributes:
        message (str): Сообщение о результате операции
        data (TableRowDataSchema): Данные строки таблицы
    """

    message: str = "Строка таблицы успешно получена"
    data: TableRowDataSchema


class TableRowListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком строк таблицы.

    Attributes:
        message (str): Сообщение о результате операции
        data (List[TableRowDataSchema]): Список данных строк таблицы
        total (int): Общее количество строк
    """

    message: str = "Список строк таблицы успешно получен"
