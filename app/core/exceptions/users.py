"""
Классы исключений для модуля users.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с пользователями.

Включают в себя:
- UserNotFoundError: Исключение, которое вызывается, когда пользователь не найден.
- UserExistsError: Исключение, которое вызывается, когда пользователь с таким именем или email уже существует.
"""

from app.core.exceptions.base import BaseAPIException


class UserInactiveError(BaseAPIException):
    """
    Пользователь не активен.

    Attributes:
        detail (str): Сообщение об ошибке.
        extra (dict): Дополнительные данные об ошибке.
    """

    def __init__(self, detail: str, extra: dict = None):
        super().__init__(
            status_code=403,
            detail=detail,
            error_type="user_inactive",
            extra=extra or {}
        )


class UserNotFoundError(BaseAPIException):
    """
    Пользователь не найден.

    Attributes:
        field (str): Поле, по которому не найден пользователь.
        value (str): Значение поля, по которому не найден пользователь.
    """

    def __init__(self, field: str, value: str):
        field_display = self._format_field_name(field)

        super().__init__(
            status_code=404,
            detail=f"Пользователь с {field_display} '{value}' не существует!",
            error_type="user_not_found",
            extra={"user_" + field: value},
        )

    def _format_field_name(self, field: str) -> str:
        match field:
            case "email":
                return "email"
            case "name":
                return "именем"
            case "phone":
                return "телефоном"
            case _:
                return field


class UserExistsError(BaseAPIException):
    """
    Пользователь с таким именем существует.

    Attributes:
        field (str): Поле, по которому существует пользователь.
        value (str): Значение поля, по которому существует пользователь.
    """

    def __init__(self, field: str, value: str):
        field_display = self._format_field_name(field)

        super().__init__(
            status_code=400,
            detail=f"Пользователь с {field_display} '{value}' существует",
            error_type="user_exists",
            extra={"user_" + field: value},
        )

    def _format_field_name(self, field: str) -> str:
        match field:
            case "email":
                return "email"
            case "name":
                return "именем"
            case "phone":
                return "телефоном"
            case _:
                return field


class UserCreationError(BaseAPIException):
    """
    Ошибка при создании пользователя.

    Attributes:
        detail (str): Подробности об ошибке.
    """

    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            detail=detail,
            error_type="user_creation_error",
            extra={}
        )
