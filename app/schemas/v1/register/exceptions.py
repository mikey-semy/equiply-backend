"""
Схемы ответов для ошибок, связанных с регистрацией пользователей.

Этот модуль содержит схемы Pydantic для структурированных ответов
при возникновении различных ошибок при регистрации.
"""

from pydantic import Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

# Пример значений для документации
EXAMPLE_TIMESTAMP = "2025-01-01T00:00:00+03:00"
EXAMPLE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


class UserExistsErrorSchema(ErrorSchema):
    """Схема ошибки существующего пользователя"""

    detail: str = "Пользователь с таким email уже существует"
    error_type: str = "user_exists"
    status_code: int = 409
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class UserExistsResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой существующего пользователя"""

    error: UserExistsErrorSchema


class UserCreationErrorSchema(ErrorSchema):
    """Схема ошибки создания пользователя"""

    detail: str = "Не удалось создать пользователя. Пожалуйста, попробуйте позже."
    error_type: str = "user_creation_error"
    status_code: int = 500
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class UserCreationResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой создания пользователя"""

    error: UserCreationErrorSchema


class TokenInvalidErrorSchema(ErrorSchema):
    """Схема ошибки недействительного токена"""

    detail: str = "Невалидный токен"
    error_type: str = "token_invalid"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class TokenInvalidResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой недействительного токена"""

    error: TokenInvalidErrorSchema


class TokenExpiredErrorSchema(ErrorSchema):
    """Схема ошибки истекшего токена"""

    detail: str = "Токен просрочен"
    error_type: str = "token_expired"
    status_code: int = 419
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class TokenExpiredResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой истекшего токена"""

    error: TokenExpiredErrorSchema
