"""Исключения для ограничения частоты запросов."""

from typing import Dict, Any, Optional

from app.core.exceptions.base import BaseAPIException

class RateLimitExceededError(BaseAPIException):
    """
    Исключение, возникающее при превышении лимита запросов.

    Attributes:
        detail (str): Сообщение об ошибке.
        error_type (str): Тип ошибки.
        status_code (int): HTTP-код состояния (429).
        extra (Dict[str, Any]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        detail: str = "Слишком много запросов. Пожалуйста, повторите попытку позже.",
        error_type: str = "rate_limit_exceeded",
        reset_time: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует исключение RateLimitExceededError.

        Args:
            detail: Сообщение об ошибке.
            error_type: Тип ошибки.
            reset_time: Время в секундах до сброса ограничения.
            extra: Дополнительная информация об ошибке.
        """
        _extra = extra or {}
        if reset_time is not None:
            _extra["reset_time"] = reset_time

        super().__init__(
            status_code=429,
            detail=detail,
            error_type=error_type,
            extra=_extra
        )
