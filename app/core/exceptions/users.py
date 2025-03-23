"""
Классы исключений для модуля users.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с пользователями.

Включают в себя:
- UserNotFoundError: Исключение, которое вызывается, когда пользователь не найден.
- UserExistsError: Исключение, которое вызывается, когда пользователь с таким именем или email уже существует.
"""

from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class ForbiddenError(BaseAPIException):
    """
    Исключение для запрещенного доступа.

    Возникает, когда у пользователя недостаточно прав для выполнения операции.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        required_role (Optional[str]): Требуемая роль для выполнения операции.
        extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
    """

    def __init__(
        self,
        detail: str = "Недостаточно прав для выполнения операции",
        required_role: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение ForbiddenError.

        Args:
            detail (str): Подробное сообщение об ошибке.
            required_role (Optional[str]): Требуемая роль для выполнения операции.
            extra_data (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
        """
        extra_data: Optional[Dict[str, Any]] = (
            {"required_role": required_role} if required_role else None
        )
        super().__init__(
            status_code=403, detail=detail, error_type="forbidden", extra=extra_data
        )


class UserNotFoundError(BaseAPIException):
    """
    Исключение для ненайденного пользователя.

    Возникает, когда запрашиваемый пользователь не найден в базе данных.

    Attributes:
        field (Optional[str]): Поле, по которому искали пользователя.
        value (Any): Значение поля, по которому искали пользователя.
        detail (Optional[str]): Подробное сообщение об ошибке.
    """

    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        """
        Инициализирует исключение UserNotFoundError.

        Args:
            field (Optional[str]): Поле, по которому искали пользователя.
            value (Any): Значение поля, по которому искали пользователя.
            detail (Optional[str]): Подробное сообщение об ошибке.
        """
        message = detail or "Пользователь не найден"
        if field and value is not None:
            message = f"Пользователь с {field}={value} не найден"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="user_not_found",
            extra={"field": field, "value": value} if field else None,
        )


class UserExistsError(BaseAPIException):
    """
    Исключение для существующего пользователя.

    Возникает при попытке создать пользователя с данными, которые уже существуют в системе.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        field (str): Поле, по которому обнаружен дубликат.
        value (Any): Значение поля, которое уже существует.
    """

    def __init__(self, field: str, value: Any):
        """
        Инициализирует исключение UserExistsError.

        Args:
            field (str): Поле, по которому обнаружен дубликат.
            value (Any): Значение поля, которое уже существует.
        """
        super().__init__(
            status_code=409,
            detail=f"Пользователь с {field}={value} уже существует",
            error_type="user_exists",
            extra={"field": field, "value": value},
        )


class UserCreationError(BaseAPIException):
    """
    Исключение при ошибке создания пользователя.

    Возникает, когда не удается создать пользователя из-за внутренней ошибки системы,
    проблем с базой данных или некорректных входных данных, которые не были
    обработаны на уровне валидации.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "user_creation_error".
        status_code (int): HTTP-код ответа - 500 (Internal Server Error).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        detail: str = "Не удалось создать пользователя. Пожалуйста, попробуйте позже.",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение UserCreationError.

        Args:
            detail (str): Подробное сообщение об ошибке. По умолчанию предоставляется
                          общее сообщение, но рекомендуется указывать более конкретную причину.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке, которая может быть полезна
                          для отладки, но не отображается в ответе клиенту.

        Examples:
            >>> raise UserCreationError("Ошибка при хешировании пароля")
            >>> raise UserCreationError("Ошибка при сохранении в базу данных", {"db_error": "Duplicate key"})
        """
        super().__init__(
            status_code=500,
            detail=detail,
            error_type="user_creation_error",
            extra=extra or {},
        )
