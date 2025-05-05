"""
Схемы ответов для ошибок, связанных с управлением группами пользователей.

Этот модуль содержит схемы Pydantic для структурированных ответов
при возникновении различных ошибок при работе с группами пользователей.
"""

from pydantic import Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema


class GroupErrorSchema(ErrorSchema):
    """
    Базовая схема ошибки для групп пользователей.

    Attributes:
        detail (str): Подробное описание ошибки.
        error_type (str): Тип ошибки.
        status_code (int): HTTP-код статуса ошибки.
    """
    detail: str = "Ошибка при работе с группой пользователей"
    error_type: str = "group_error"
    status_code: int = 400


class GroupErrorResponseSchema(ErrorResponseSchema):
    """
    Базовая схема ответа с ошибкой для групп пользователей.

    Attributes:
        error (GroupErrorSchema): Данные об ошибке.
    """
    error: GroupErrorSchema = Field(default_factory=GroupErrorSchema)


class GroupNotFoundErrorSchema(ErrorSchema):
    """
    Схема ошибки ненайденной группы.

    Attributes:
        detail (str): Подробное описание ошибки.
        error_type (str): Тип ошибки.
        status_code (int): HTTP-код статуса ошибки.
    """
    detail: str = "Группа не найдена"
    error_type: str = "group_not_found"
    status_code: int = 404


class GroupNotFoundResponseSchema(ErrorResponseSchema):
    """
    Схема ответа с ошибкой ненайденной группы.

    Attributes:
        error (GroupNotFoundErrorSchema): Данные об ошибке.
    """
    error: GroupNotFoundErrorSchema = Field(default_factory=GroupNotFoundErrorSchema)


class UserAlreadyInGroupErrorSchema(ErrorSchema):
    """
    Схема ошибки, когда пользователь уже в группе.

    Attributes:
        detail (str): Подробное описание ошибки.
        error_type (str): Тип ошибки.
        status_code (int): HTTP-код статуса ошибки.
    """
    detail: str = "Пользователь уже состоит в группе"
    error_type: str = "user_already_in_group"
    status_code: int = 400


class UserAlreadyInGroupResponseSchema(ErrorResponseSchema):
    """
    Схема ответа с ошибкой, когда пользователь уже в группе.

    Attributes:
        error (UserAlreadyInGroupErrorSchema): Данные об ошибке.
    """
    error: UserAlreadyInGroupErrorSchema = Field(default_factory=UserAlreadyInGroupErrorSchema)


class UserNotInGroupErrorSchema(ErrorSchema):
    """
    Схема ошибки, когда пользователь не в группе.

    Attributes:
        detail (str): Подробное описание ошибки.
        error_type (str): Тип ошибки.
        status_code (int): HTTP-код статуса ошибки.
    """
    detail: str = "Пользователь не состоит в группе"
    error_type: str = "user_not_in_group"
    status_code: int = 400


class UserNotInGroupResponseSchema(ErrorResponseSchema):
    """
    Схема ответа с ошибкой, когда пользователь не в группе.

    Attributes:
        error (UserNotInGroupErrorSchema): Данные об ошибке.
    """
    error: UserNotInGroupErrorSchema = Field(default_factory=UserNotInGroupErrorSchema)
