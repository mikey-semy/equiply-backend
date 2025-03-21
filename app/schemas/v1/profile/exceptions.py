"""
Схемы ответов для ошибок, связанных с профилем пользователя.

Этот модуль содержит схемы Pydantic для структурированных ответов
при возникновении различных ошибок при работе с профилем.
"""

from pydantic import Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

# Пример значений для документации
EXAMPLE_TIMESTAMP = "2025-01-01T00:00:00+03:00"
EXAMPLE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


class ProfileNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденного профиля"""

    detail: str = "Профиль не найден"
    error_type: str = "profile_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class ProfileNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденного профиля"""

    error: ProfileNotFoundErrorSchema


class InvalidCurrentPasswordErrorSchema(ErrorSchema):
    """Схема ошибки неверного текущего пароля"""

    detail: str = "Текущий пароль неверен"
    error_type: str = "invalid_current_password"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class InvalidCurrentPasswordResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой неверного текущего пароля"""

    error: InvalidCurrentPasswordErrorSchema


class UserNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденного пользователя"""

    detail: str = "Пользователь не найден"
    error_type: str = "user_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class UserNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденного пользователя"""

    error: UserNotFoundErrorSchema


class InvalidFileTypeErrorSchema(ErrorSchema):
    """Схема ошибки неверного типа файла"""

    detail: str = "Неверный тип файла. Поддерживаются только JPEG и PNG"
    error_type: str = "invalid_file_type"
    status_code: int = 415
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class InvalidFileTypeResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой неверного типа файла"""

    error: InvalidFileTypeErrorSchema


class FileTooLargeErrorSchema(ErrorSchema):
    """Схема ошибки слишком большого файла"""

    detail: str = "Размер файла превышает допустимый лимит (2MB)"
    error_type: str = "file_too_large"
    status_code: int = 413
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class FileTooLargeResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой слишком большого файла"""

    error: FileTooLargeErrorSchema


class StorageErrorSchema(ErrorSchema):
    """Схема ошибки хранилища"""

    detail: str = "Ошибка при загрузке файла в хранилище"
    error_type: str = "storage_error"
    status_code: int = 500
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class StorageErrorResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой хранилища"""

    error: StorageErrorSchema
