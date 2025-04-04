"""
Классы исключений для модуля канбан-досок.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с канбан-досками.

Включают в себя:
- KanbanBoardNotFoundError: Исключение, когда канбан-доска не найдена.
- KanbanBoardAccessDeniedError: Исключение, когда доступ к канбан-доске запрещен.
- KanbanColumnNotFoundError: Исключение, когда колонка канбан-доски не найдена.
- KanbanCardNotFoundError: Исключение, когда карточка канбан-доски не найдена.
"""

from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class KanbanBoardNotFoundError(BaseAPIException):
    """
    Исключение для ненайденной канбан-доски.

    Возникает, когда запрашиваемая канбан-доска не найдена в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        board_id (int): ID канбан-доски, которая не найдена.
    """

    def __init__(
        self, board_id: Optional[int] = None, detail: Optional[str] = None
    ):
        """
        Инициализирует исключение KanbanBoardNotFoundError.

        Args:
            board_id (int): ID канбан-доски, которая не найдена.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Канбан-доска не найдена"
        if board_id is not None:
            message = f"Канбан-доска с ID={board_id} не найдена"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="kanban_board_not_found",
            extra={"board_id": board_id} if board_id is not None else None,
        )


class KanbanBoardAccessDeniedError(BaseAPIException):
    """
    Исключение для отказа в доступе к канбан-доске.

    Возникает, когда у пользователя недостаточно прав для выполнения операции
    с канбан-доской.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        board_id (int): ID канбан-доски.
    """

    def __init__(
        self,
        board_id: Optional[int] = None,
        detail: Optional[str] = None,
    ):
        """
        Инициализирует исключение KanbanBoardAccessDeniedError.

        Args:
            board_id (int): ID канбан-доски.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Доступ к канбан-доске запрещен"

        extra: Dict[str, Any] = {}
        if board_id is not None:
            extra["board_id"] = board_id

        super().__init__(
            status_code=403,
            detail=message,
            error_type="kanban_board_access_denied",
            extra=extra if extra else None,
        )


class KanbanColumnNotFoundError(BaseAPIException):
    """
    Исключение для ненайденной колонки канбан-доски.

    Возникает, когда запрашиваемая колонка не найдена в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        column_id (int): ID колонки, которая не найдена.
    """

    def __init__(
        self, column_id: Optional[int] = None, detail: Optional[str] = None
    ):
        """
        Инициализирует исключение KanbanColumnNotFoundError.

        Args:
            column_id (int): ID колонки, которая не найдена.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Колонка канбан-доски не найдена"
        if column_id is not None:
            message = f"Колонка канбан-доски с ID={column_id} не найдена"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="kanban_column_not_found",
            extra={"column_id": column_id} if column_id is not None else None,
        )


class KanbanCardNotFoundError(BaseAPIException):
    """
    Исключение для ненайденной карточки канбан-доски.

    Возникает, когда запрашиваемая карточка не найдена в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        card_id (int): ID карточки, которая не найдена.
    """

    def __init__(
        self, card_id: Optional[int] = None, detail: Optional[str] = None
    ):
        """
        Инициализирует исключение KanbanCardNotFoundError.

        Args:
            card_id (int): ID карточки, которая не найдена.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Карточка канбан-доски не найдена"
        if card_id is not None:
            message = f"Карточка канбан-доски с ID={card_id} не найдена"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="kanban_card_not_found",
            extra={"card_id": card_id} if card_id is not None else None,
        )
