from pydantic import Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

# Пример значений для документации
EXAMPLE_TIMESTAMP = "2025-01-01T00:00:00+03:00"
EXAMPLE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


class KanbanBoardNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденной канбан-доски"""

    detail: str = "Канбан-доска не найдена"
    error_type: str = "kanban_board_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class KanbanBoardNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденной канбан-доски"""

    error: KanbanBoardNotFoundErrorSchema


class KanbanColumnNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденной колонки канбан-доски"""

    detail: str = "Колонка канбан-доски не найдена"
    error_type: str = "kanban_column_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class KanbanColumnNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденной колонки канбан-доски"""

    error: KanbanColumnNotFoundErrorSchema


class KanbanCardNotFoundErrorSchema(ErrorSchema):
    """Схема ошибки ненайденной карточки канбан-доски"""

    detail: str = "Карточка канбан-доски не найдена"
    error_type: str = "kanban_card_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class KanbanCardNotFoundResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой ненайденной карточки канбан-доски"""

    error: KanbanCardNotFoundErrorSchema


class KanbanAccessDeniedErrorSchema(ErrorSchema):
    """Схема ошибки отказа в доступе к канбан-доске"""

    detail: str = "Доступ к канбан-доске запрещен"
    error_type: str = "kanban_access_denied"
    status_code: int = 403
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class KanbanAccessDeniedResponseSchema(ErrorResponseSchema):
    """Схема ответа с ошибкой отказа в доступе к канбан-доске"""

    error: KanbanAccessDeniedErrorSchema
