"""
Исключения, связанные с модулем таблиц.

Этот модуль содержит иерархию исключений для обработки различных ошибок,
связанных с таблицами и их данными.

Иерархия исключений:
1. BaseAPIException (основной класс для всех API-исключений)
   └── TableError (базовый класс для ошибок таблиц)
       ├── TableNotFoundError (таблица не найдена)
       ├── TableRowNotFoundError (строка таблицы не найдена)
       ├── InvalidTableSchemaError (невалидная схема таблицы)
       ├── InvalidTableDataError (невалидные данные таблицы)
       └── TableImportExportError (базовый класс для ошибок импорта/экспорта)
           ├── InvalidFileFormatError (неверный формат файла)
           ├── MissingRequiredColumnsError (отсутствуют обязательные столбцы)
           └── DataConversionError (ошибка преобразования данных)
"""

from typing import Any, Dict, List, Optional

from app.core.exceptions.base import BaseAPIException

class TableError(BaseAPIException):
    """
    Базовый класс для всех ошибок, связанных с таблицами.

    Этот класс устанавливает код статуса HTTP 400 (Bad Request) и предоставляет
    базовую структуру для всех исключений, связанных с таблицами.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки для классификации на стороне клиента.
        extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
        status_code (int): HTTP-код состояния (400 для ошибок таблиц).
    """

    def __init__(
        self,
        detail: str = "Ошибка таблицы",
        error_type: str = "table_error",
        status_code: int = 400,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение TableError.

        Args:
            detail (str): Подробное сообщение об ошибке.
            error_type (str): Тип ошибки для классификации.
            status_code (int): HTTP-код состояния.
            extra (dict): Дополнительные данные об ошибке.
        """
        super().__init__(
            status_code=status_code,
            detail=detail,
            error_type=error_type,
            extra=extra or {},
        )

class TableNotFoundError(TableError):
    """
    Исключение для ненайденной таблицы.

    Возникает, когда запрашиваемая таблица не найдена в базе данных.

    Attributes:
        detail (str): Сообщение с указанием ID ненайденной таблицы.
        error_type (str): "table_not_found".
        status_code (int): 404 (Not Found).
        extra (dict): Содержит ID таблицы в ключе "table_id".
    """

    def __init__(self, table_id: int):
        """
        Инициализирует исключение TableNotFoundError.

        Args:
            table_id (int): ID ненайденной таблицы.
        """
        super().__init__(
            detail=f"Таблица с ID {table_id} не найдена",
            error_type="table_not_found",
            status_code=404,
            extra={"table_id": table_id},
        )


class TableRowNotFoundError(TableError):
    """
    Исключение для ненайденной строки таблицы.

    Возникает, когда запрашиваемая строка таблицы не найдена в базе данных.

    Attributes:
        detail (str): Сообщение с указанием ID ненайденной строки.
        error_type (str): "table_row_not_found".
        status_code (int): 404 (Not Found).
        extra (dict): Содержит ID строки в ключе "row_id" и ID таблицы в ключе "table_id".
    """

    def __init__(self, row_id: int, table_id: Optional[int] = None):
        """
        Инициализирует исключение TableRowNotFoundError.

        Args:
            row_id (int): ID ненайденной строки.
            table_id (Optional[int]): ID таблицы, если известен.
        """
        extra = {"row_id": row_id}
        if table_id is not None:
            extra["table_id"] = table_id

        super().__init__(
            detail=f"Строка с ID {row_id} не найдена",
            error_type="table_row_not_found",
            status_code=404,
            extra=extra,
        )


class InvalidTableSchemaError(TableError):
    """
    Исключение для невалидной схемы таблицы.

    Возникает при попытке создать или обновить таблицу с невалидной схемой.

    Attributes:
        detail (str): Сообщение с описанием проблемы в схеме.
        error_type (str): "invalid_table_schema".
        status_code (int): 400 (Bad Request).
        extra (dict): Содержит детали ошибок валидации.
    """

    def __init__(self, errors: List[str]):
        """
        Инициализирует исключение InvalidTableSchemaError.

        Args:
            errors (List[str]): Список ошибок валидации схемы.
        """
        detail = "Невалидная схема таблицы"
        if errors:
            detail += f": {'; '.join(errors)}"

        super().__init__(
            detail=detail,
            error_type="invalid_table_schema",
            status_code=400,
            extra={"validation_errors": errors},
        )


class InvalidTableDataError(TableError):
    """
    Исключение для невалидных данных таблицы.

    Возникает при попытке добавить или обновить данные, не соответствующие схеме таблицы.

    Attributes:
        detail (str): Сообщение с описанием проблемы в данных.
        error_type (str): "invalid_table_data".
        status_code (int): 400 (Bad Request).
        extra (dict): Содержит детали ошибок валидации.
    """

    def __init__(self, errors: List[str]):
        """
        Инициализирует исключение InvalidTableDataError.

        Args:
            errors (List[str]): Список ошибок валидации данных.
        """
        detail = "Невалидные данные таблицы"
        if errors:
            detail += f": {'; '.join(errors)}"

        super().__init__(
            detail=detail,
            error_type="invalid_table_data",
            status_code=400,
            extra={"validation_errors": errors},
        )

class TableImportExportError(TableError):
    """
    Базовый класс для ошибок импорта/экспорта таблиц.

    Предоставляет общую структуру для ошибок, возникающих при импорте или экспорте данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки для классификации.
        status_code (int): HTTP-код состояния (400 для ошибок импорта/экспорта).
        extra (dict): Дополнительные данные об ошибке.
    """

    def __init__(
        self,
        detail: str = "Ошибка импорта/экспорта таблицы",
        error_type: str = "table_import_export_error",
        status_code: int = 400,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение TableImportExportError.

        Args:
            detail (str): Подробное сообщение об ошибке.
            error_type (str): Тип ошибки для классификации.
            status_code (int): HTTP-код состояния.
            extra (dict): Дополнительные данные об ошибке.
        """
        super().__init__(
            detail=detail,
            error_type=error_type,
            status_code=status_code,
            extra=extra or {},
        )

class InvalidFileFormatError(TableImportExportError):
    """
    Исключение для неверного формата файла.

    Возникает при попытке импортировать файл неподдерживаемого формата.

    Attributes:
        detail (str): Сообщение с указанием неверного формата.
        error_type (str): "invalid_file_format".
        extra (dict): Содержит имя файла и его формат.
    """

    def __init__(self, filename: str, expected_format: str = "Excel (.xlsx, .xls)"):
        """
        Инициализирует исключение InvalidFileFormatError.

        Args:
            filename (str): Имя файла с неверным форматом.
            expected_format (str): Ожидаемый формат файла.
        """
        super().__init__(
            detail=f"Неверный формат файла: {filename}. Ожидается {expected_format}",
            error_type="invalid_file_format",
            extra={"filename": filename, "expected_format": expected_format},
        )

class MissingRequiredColumnsError(TableImportExportError):
    """
    Исключение для отсутствующих обязательных столбцов.

    Возникает при импорте данных, когда в файле отсутствуют обязательные столбцы.

    Attributes:
        detail (str): Сообщение с указанием отсутствующих столбцов.
        error_type (str): "missing_required_columns".
        extra (dict): Содержит список отсутствующих столбцов.
    """

    def __init__(self, missing_columns: List[str]):
        """
        Инициализирует исключение MissingRequiredColumnsError.

        Args:
            missing_columns (List[str]): Список отсутствующих обязательных столбцов.
        """
        super().__init__(
            detail=f"Отсутствуют обязательные столбцы: {', '.join(missing_columns)}",
            error_type="missing_required_columns",
            extra={"missing_columns": missing_columns},
        )

class DataConversionError(TableImportExportError):
    """
    Исключение для ошибок преобразования данных.

    Возникает при импорте данных, когда значения не могут быть преобразованы в нужный тип.

    Attributes:
        detail (str): Сообщение с описанием ошибок преобразования.
        error_type (str): "data_conversion_error".
        extra (dict): Содержит список ошибок преобразования.
    """

    def __init__(self, errors: List[str]):
        """
        Инициализирует исключение DataConversionError.

        Args:
            errors (List[str]): Список ошибок преобразования данных.
        """
        detail = "Ошибки преобразования данных"
        if errors:
            detail += f": {'; '.join(errors[:5])}"
            if len(errors) > 5:
                detail += f" и еще {len(errors) - 5} ошибок"

        super().__init__(
            detail=detail,
            error_type="data_conversion_error",
            extra={"conversion_errors": errors},
        )

class TableTemplateNotFoundError(BaseAPIException):
    """
    Исключение для ненайденного шаблона таблицы.

    Возникает, когда запрашиваемый шаблон таблицы не найден в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        template_id (int): ID шаблона, который не найден.
    """

    def __init__(self, template_id: Optional[int] = None, detail: Optional[str] = None):
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
