from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class AccessControlException(BaseAPIException):
    """
    Базовое исключение для ошибок контроля доступа.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_code (str): Код ошибки.
        status_code (int): HTTP-код статуса.
        extra (Dict[str, Any]): Дополнительная информация об ошибке.
    """

    status_code = 403
    error_code = "access_control_error"
    detail = "Ошибка контроля доступа"


class AccessDeniedException(AccessControlException):
    """
    Исключение, возникающее при отказе в доступе.
    """

    error_code = "access_denied"
    detail = "Доступ запрещен"

    def __init__(
        self, message: Optional[str] = None, extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(detail=message or self.detail, extra=extra)


class PolicyNotFoundException(AccessControlException):
    """
    Исключение, возникающее при попытке получить несуществующую политику.
    """

    status_code = 404
    error_code = "policy_not_found"
    detail = "Политика доступа не найдена"


class RuleNotFoundException(AccessControlException):
    """
    Исключение, возникающее при попытке получить несуществующее правило.
    """

    status_code = 404
    error_code = "rule_not_found"
    detail = "Правило доступа не найдено"


class InvalidPolicyDataException(AccessControlException):
    """
    Исключение, возникающее при попытке создать или обновить политику с некорректными данными.
    """

    status_code = 400
    error_code = "invalid_policy_data"
    detail = "Некорректные данные политики доступа"


class InvalidRuleDataException(AccessControlException):
    """
    Исключение, возникающее при попытке создать или обновить правило с некорректными данными.
    """

    status_code = 400
    error_code = "invalid_rule_data"
    detail = "Некорректные данные правила доступа"
