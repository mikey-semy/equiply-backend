"""
Классы исключений для модуля AI.

Этот модуль содержит классы исключений, которые могут быть вызваны
при работе с AI сервисами и интеграциями.

Включают в себя:
- AIError: Базовое исключение для всех ошибок AI.
- AICompletionError: Исключение при ошибке получения ответа от AI.
- AIConfigError: Исключение при ошибке конфигурации AI.
- AIAuthError: Исключение при ошибке авторизации в API AI.
- AIHistoryNotFoundError: Исключение при отсутствии истории чата.
- AIHistoryExportError: Исключение при ошибке экспорта истории чата.
"""

from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class AIError(BaseAPIException):
    """
    Базовое исключение для всех ошибок AI.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки.
        status_code (int): HTTP-код ответа.
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        message: str,
        error_type: str,
        status_code: int = 400,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение AIError.

        Args:
            message (str): Сообщение об ошибке.
            error_type (str): Тип ошибки.
            status_code (int): HTTP-код ответа.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            status_code=status_code, detail=message, error_type=error_type, extra=extra
        )


class AICompletionError(AIError):
    """
    Исключение при ошибке получения ответа от AI.

    Возникает, когда не удается получить ответ от AI модели из-за проблем
    с API, сетевых ошибок или некорректных входных данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "ai_completion_error".
        status_code (int): HTTP-код ответа - 500 (Internal Server Error).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Инициализирует исключение AICompletionError.

        Args:
            message (str): Сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            message=f"Ошибка при получении ответа от AI: {message}",
            error_type="ai_completion_error",
            status_code=500,
            extra=extra,
        )


class AIConfigError(AIError):
    """
    Исключение при ошибке конфигурации AI.

    Возникает при проблемах с настройками AI, некорректных параметрах
    или отсутствии необходимых конфигурационных данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "ai_config_error".
        status_code (int): HTTP-код ответа - 500 (Internal Server Error).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Инициализирует исключение AIConfigError.

        Args:
            message (str): Сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            message=f"Ошибка конфигурации AI: {message}",
            error_type="ai_config_error",
            status_code=500,
            extra=extra,
        )


class AIAuthError(AIError):
    """
    Исключение при ошибке авторизации в API AI.

    Возникает при проблемах с аутентификацией в API AI,
    недействительных или отсутствующих ключах API.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "ai_auth_error".
        status_code (int): HTTP-код ответа - 401 (Unauthorized).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        message: str = "Ошибка авторизации в API",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение AIAuthError.

        Args:
            message (str): Сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            message=message, error_type="ai_auth_error", status_code=401, extra=extra
        )


class AIHistoryNotFoundError(AIError):
    """
    Исключение при отсутствии истории чата.

    Возникает, когда запрашиваемая история чата не найдена в хранилище.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "ai_history_not_found".
        status_code (int): HTTP-код ответа - 404 (Not Found).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        message: str = "История чата не найдена",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение AIHistoryNotFoundError.

        Args:
            message (str): Сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            message=message,
            error_type="ai_history_not_found",
            status_code=404,
            extra=extra,
        )


class AIHistoryExportError(AIError):
    """
    Исключение при ошибке экспорта истории чата.

    Возникает при проблемах с экспортом истории чата в различные форматы.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "ai_history_export_error".
        status_code (int): HTTP-код ответа - 500 (Internal Server Error).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        message: str = "Ошибка при экспорте истории чата",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение AIHistoryExportError.

        Args:
            message (str): Сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            message=message,
            error_type="ai_history_export_error",
            status_code=500,
            extra=extra,
        )


class AIChatNotFoundError(AIError):
    """
    Исключение при отсутствии чата.

    Возникает, когда запрашиваемый чат не найден в хранилище.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "ai_chat_not_found".
        status_code (int): HTTP-код ответа - 404 (Not Found).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self, message: str = "Чат не найден", extra: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует исключение AIChatNotFoundError.

        Args:
            message (str): Сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            message=message,
            error_type="ai_chat_not_found",
            status_code=404,
            extra=extra,
        )


class AIChatAccessError(AIError):
    """
    Исключение при попытке доступа к чужому чату.

    Возникает, когда пользователь пытается получить доступ к чату другого пользователя.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "ai_chat_access_error".
        status_code (int): HTTP-код ответа - 403 (Forbidden).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        message: str = "Доступ к чату запрещен",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение AIChatAccessError.

        Args:
            message (str): Сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            message=message,
            error_type="ai_chat_access_error",
            status_code=403,
            extra=extra,
        )


class AIChatDuplicateError(AIError):
    """
    Исключение при попытке создать дублирующийся чат.

    Возникает, когда пользователь пытается создать чат с уже существующим названием.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "ai_chat_duplicate_error".
        status_code (int): HTTP-код ответа - 409 (Conflict).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        message: str = "Чат с таким названием уже существует",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение AIChatDuplicateError.

        Args:
            message (str): Сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        super().__init__(
            message=message,
            error_type="ai_chat_duplicate_error",
            status_code=409,
            extra=extra,
        )
