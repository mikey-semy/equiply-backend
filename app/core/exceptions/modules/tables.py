"""
Классы исключений для модуля таблиц.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с таблицами.

Включают в себя:
- TableNotFoundError: Исключение, которое вызывается, когда таблица не найдена.
- TableRowNotFoundError: Исключение, которое вызывается, когда строка таблицы не найдена.
- InvalidTableSchemaError: Исключение, которое вызывается, когда схема таблицы невалидна.
- InvalidTableDataError: Исключение, которое вызывается, когда данные таблицы невалидны.
"""

from app.core.exceptions.base import BaseAPIException


class TableNotFoundError(BaseAPIException):
    """
    Исключение для ненайденной таблицы.

    Возникает, когда запрашиваемая таблица не найдена в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        table_id (int): ID таблицы, которая не найдена.
    """

    def __init__(self, table_id: int = None, detail: str = None):
        """
        Инициализирует исключение TableNotFoundError.

        Args:
            table_id (int): ID таблицы, которая не найдена.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Таблица не найдена"
        if table_id is not None:
            message = f"Таблица с ID={table_id} не найдена"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="table_not_found",
            extra={"table_id": table_id} if table_id is not None else None,
        )


class TableRowNotFoundError(BaseAPIException):
    """
    Исключение для ненайденной строки таблицы.

    Возникает, когда запрашиваемая строка таблицы не найдена в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        row_id (int): ID строки, которая не найдена.
        table_id (int): ID таблицы, в которой искали строку.
    """

    def __init__(self, row_id: int = None, table_id: int = None, detail: str = None):
        """
        Инициализирует исключение TableRowNotFoundError.

        Args:
            row_id (int): ID строки, которая не найдена.
            table_id (int): ID таблицы, в которой искали строку.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Строка таблицы не найдена"
        if row_id is not None:
            message = f"Строка с ID={row_id} не найдена"
            if table_id is not None:
                message = f"Строка с ID={row_id} не найдена в таблице с ID={table_id}"

        extra = {}
        if row_id is not None:
            extra["row_id"] = row_id
        if table_id is not None:
            extra["table_id"] = table_id

        super().__init__(
            status_code=404,
            detail=message,
            error_type="table_row_not_found",
            extra=extra if extra else None,
        )


class InvalidTableSchemaError(BaseAPIException):
    """
    Исключение для невалидной схемы таблицы.

    Возникает, когда предоставленная схема таблицы не соответствует требованиям.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        errors (list): Список ошибок валидации.
    """

    def __init__(self, detail: str = "Невалидная схема таблицы", errors: list = None):
        """
        Инициализирует исключение InvalidTableSchemaError.

        Args:
            detail (str): Подробное сообщение об ошибке.
            errors (list): Список ошибок валидации.
        """
        super().__init__(
            status_code=400,
            detail=detail,
            error_type="invalid_table_schema",
            extra={"errors": errors} if errors else None,
        )


class InvalidTableDataError(BaseAPIException):
    """
    Исключение для невалидных данных таблицы.

    Возникает, когда предоставленные данные для строки таблицы не соответствуют схеме.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        errors (list): Список ошибок валидации.
        field (str): Поле, в котором обнаружена ошибка.
    """

    def __init__(
        self,
        detail: str = "Невалидные данные таблицы",
        errors: list = None,
        field: str = None,
    ):
        """
        Инициализирует исключение InvalidTableDataError.

        Args:
            detail (str): Подробное сообщение об ошибке.
            errors (list): Список ошибок валидации.
            field (str): Поле, в котором обнаружена ошибка.
        """
        extra = {}
        if errors:
            extra["errors"] = errors
        if field:
            extra["field"] = field

        super().__init__(
            status_code=400,
            detail=detail,
            error_type="invalid_table_data",
            extra=extra if extra else None,
        )


class TableTemplateNotFoundError(BaseAPIException):
    """
    Исключение для ненайденного шаблона таблицы.

    Возникает, когда запрашиваемый шаблон таблицы не найден в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        template_id (int): ID шаблона, который не найден.
    """

    def __init__(self, template_id: int = None, detail: str = None):
        """
        Инициализирует исключение TableTemplateNotFoundError.

        Args:
            template_id (int): ID шаблона, который не найден.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Шаблон таблицы не найден"
        if template_id is not None:
            message = f"Шаблон таблицы с ID={template_id} не найден"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="table_template_not_found",
            extra={"template_id": template_id} if template_id is not None else None,
        )
