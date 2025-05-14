"""
Схемы ответов для ошибок, связанных с модулем таблиц.

Этот модуль содержит схемы Pydantic для структурированных ответов
при возникновении различных ошибок при работе с таблицами.
"""

from pydantic import Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

# Пример значений для документации
EXAMPLE_TIMESTAMP = "2025-01-01T00:00:00+03:00"
EXAMPLE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


class TableNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденной таблицы"""

    detail: str = "Таблица не найдена"
    error_type: str = "table_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class TableNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденной таблицы"""

    error: TableNotFoundErrorSchema


class TableRowNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденной строки таблицы"""

    detail: str = "Строка таблицы не найдена"
    error_type: str = "table_row_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class TableRowNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденной строки таблицы"""

    error: TableRowNotFoundErrorSchema


class InvalidTableSchemaErrorSchema(ErrorSchema):
    """Схема ошибки невалидной схемы таблицы"""

    detail: str = "Невалидная схема таблицы"
    error_type: str = "invalid_table_schema"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class InvalidTableSchemaResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой невалидной схемы таблицы"""

    error: InvalidTableSchemaErrorSchema


class InvalidTableDataErrorSchema(ErrorSchema):
    """Схема ошибки невалидных данных таблицы"""

    detail: str = "Невалидные данные таблицы"
    error_type: str = "invalid_table_data"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class InvalidTableDataResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой невалидных данных таблицы"""

    error: InvalidTableDataErrorSchema


class TableTemplateNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденного шаблона таблицы"""

    detail: str = "Шаблон таблицы не найден"
    error_type: str = "table_template_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class TableTemplateNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденного шаблона таблицы"""

    error: TableTemplateNotFoundErrorSchema

class InvalidFileFormatErrorSchema(ErrorSchema):
    """Схема ошибки неверного формата файла"""

    detail: str = "Неверный формат файла"
    error_type: str = "invalid_file_format"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class InvalidFileFormatResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой неверного формата файла"""

    error: InvalidFileFormatErrorSchema

class MissingRequiredColumnsErrorSchema(ErrorSchema):
    """Схема ошибки отсутствия обязательных столбцов"""

    detail: str = "Отсутствуют обязательные столбцы"
    error_type: str = "missing_required_columns"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class MissingRequiredColumnsResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой отсутствия обязательных столбцов"""

    error: MissingRequiredColumnsErrorSchema


class DataConversionErrorSchema(ErrorSchema):
    """Схема ошибки преобразования данных"""

    detail: str = "Ошибки преобразования данных"
    error_type: str = "data_conversion_error"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class DataConversionResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой преобразования данных"""

    error: DataConversionErrorSchema


class TableImportExportErrorSchema(ErrorSchema):
    """Схема ошибки импорта/экспорта таблицы"""

    detail: str = "Ошибка импорта/экспорта таблицы"
    error_type: str = "table_import_export_error"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class TableImportExportResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой импорта/экспорта таблицы"""

    error: TableImportExportErrorSchema