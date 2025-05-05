"""
Схемы ответов для ошибок, связанных с управлением пользователями.

Этот модуль содержит схемы Pydantic для структурированных ответов
при возникновении различных ошибок при работе с пользователями.
"""

from pydantic import  Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

# Пример значений для документации
EXAMPLE_TIMESTAMP = "2025-01-01T00:00:00+03:00"
EXAMPLE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


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


class UnauthorizedErrorSchema(ErrorSchema):
    """Схема ошибки неавторизованного доступа"""

    detail: str = "Необходима авторизация"
    error_type: str = "unauthorized"
    status_code: int = 401
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class UnauthorizedResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой неавторизованного доступа"""

    error: UnauthorizedErrorSchema


class ForbiddenErrorSchema(ErrorSchema):
    """Схема ошибки запрещенного доступа"""

    detail: str = "Недостаточно прав для выполнения операции"
    error_type: str = "forbidden"
    status_code: int = 403
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class ForbiddenResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой запрещенного доступа"""

    error: ForbiddenErrorSchema
