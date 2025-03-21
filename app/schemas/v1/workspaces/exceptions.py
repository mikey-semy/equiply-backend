"""
Схемы ответов для ошибок, связанных с модулем рабочих пространств.

Этот модуль содержит схемы Pydantic для структурированных ответов
при возникновении различных ошибок при работе с рабочими пространствами.
"""

from pydantic import Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

# Пример значений для документации
EXAMPLE_TIMESTAMP = "2025-01-01T00:00:00+03:00"
EXAMPLE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


class WorkspaceNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденного рабочего пространства"""

    detail: str = "Рабочее пространство не найдено"
    error_type: str = "workspace_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class WorkspaceNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденного рабочего пространства"""

    error: WorkspaceNotFoundErrorSchema


class WorkspaceMemberNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденного участника рабочего пространства"""

    detail: str = "Участник рабочего пространства не найден"
    error_type: str = "workspace_member_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class WorkspaceMemberNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденного участника рабочего пространства"""

    error: WorkspaceMemberNotFoundErrorSchema


class WorkspaceAccessDeniedErrorSchema(ErrorSchema):
    """Схема ошибки отказа в доступе к рабочему пространству"""

    detail: str = "Доступ к рабочему пространству запрещен"
    error_type: str = "workspace_access_denied"
    status_code: int = 403
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class WorkspaceAccessDeniedResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой отказа в доступе к рабочему пространству"""

    error: WorkspaceAccessDeniedErrorSchema
