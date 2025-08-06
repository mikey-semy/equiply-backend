"""
Исключения, связанные с управлением группами пользователей.

Этот модуль содержит иерархию исключений для обработки различных ошибок,
связанных с группами пользователей в приложении.

Иерархия исключений:
1. BaseAPIException (основной класс для всех API-исключений)
   └── GroupException (базовый класс для ошибок групп)
       ├── GroupNotFoundException (группа не найдена)
       ├── UserAlreadyInGroupException (пользователь уже в группе)
       └── UserNotInGroupException (пользователь не в группе)

Все исключения наследуются от BaseAPIException, который предоставляет
общую структуру для HTTP-ответов об ошибках, включая статус-код,
детальное сообщение, тип ошибки и дополнительные данные.

Пример использования:
```python
# Проверка существования группы
if not group_exists(group_id):
    raise GroupNotFoundException(group_id)

# Проверка членства пользователя в группе
if is_user_in_group(user_id, group_id):
    raise UserAlreadyInGroupException(user_id, group_id)

# Проверка отсутствия пользователя в группе
if not is_user_in_group(user_id, group_id):
    raise UserNotInGroupException(user_id, group_id)
"""
import uuid
from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class GroupException(BaseAPIException):
    """
    Базовый класс для всех ошибок, связанных с группами пользователей.

    Этот класс устанавливает код статуса HTTP 400 (Bad Request) и предоставляет
    базовую структуру для всех исключений, связанных с группами пользователей.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки для классификации на стороне клиента.
        extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
        status_code (int): HTTP-код состояния (400 для ошибок групп).
    """

    def __init__(
        self,
        detail: str = "Ошибка при работе с группой пользователей",
        error_type: str = "group_error",
        status_code: int = 400,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение GroupException.

        Args:
            detail (str): Подробное сообщение об ошибке.
            error_type (str): Тип ошибки для классификации.
            status_code (int): HTTP-код состояния.
            extra (dict): Дополнительные данные об ошибке.
        """
        super().__init__(
            status_code=status_code,
            detail=detail,
            error_type=error_type,
            extra=extra or {},
        )


class GroupNotFoundException(GroupException):
    """
    Исключение для ненайденной группы.

    Возникает, когда запрашиваемая группа не найдена в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "group_not_found".
        status_code (int): HTTP-код ответа - 404 (Not Found).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        group_id: Optional[int] = None,
        detail: str = "Группа не найдена",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение GroupNotFoundException.

        Args:
            group_id (Optional[int]): ID группы, которая не найдена.
            detail (str): Подробное сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        message = detail
        if group_id is not None:
            message = f"Группа с ID {group_id} не найдена"

        extra_data = extra or {}
        if group_id is not None:
            extra_data["group_id"] = group_id

        super().__init__(
            status_code=404,
            detail=message,
            error_type="group_not_found",
            extra=extra_data,
        )


class UserAlreadyInGroupException(GroupException):
    """
    Исключение, когда пользователь уже состоит в группе.

    Возникает при попытке добавить пользователя в группу, в которой он уже состоит.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "user_already_in_group".
        status_code (int): HTTP-код ответа - 400 (Bad Request).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        user_id: Optional[uuid.UUID] = None,
        group_id: Optional[int] = None,
        detail: str = "Пользователь уже состоит в группе",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение UserAlreadyInGroupException.

        Args:
            user_id (Optional[UUID]): ID пользователя.
            group_id (Optional[int]): ID группы.
            detail (str): Подробное сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        message = detail
        if user_id is not None and group_id is not None:
            message = f"Пользователь с ID {user_id} уже состоит в группе с ID {group_id}"

        extra_data = extra or {}
        if user_id is not None:
            extra_data["user_id"] = user_id
        if group_id is not None:
            extra_data["group_id"] = group_id

        super().__init__(
            status_code=400,
            detail=message,
            error_type="user_already_in_group",
            extra=extra_data,
        )


class UserNotInGroupException(GroupException):
    """
    Исключение, когда пользователь не состоит в группе.

    Возникает при попытке выполнить операцию, требующую членства пользователя в группе,
    когда пользователь не является членом этой группы.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        error_type (str): Тип ошибки - "user_not_in_group".
        status_code (int): HTTP-код ответа - 400 (Bad Request).
        extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
    """

    def __init__(
        self,
        user_id: Optional[uuid.UUID] = None,
        group_id: Optional[int] = None,
        detail: str = "Пользователь не состоит в группе",
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализирует исключение UserNotInGroupException.

        Args:
            user_id (Optional[UUID]): ID пользователя.
            group_id (Optional[int]): ID группы.
            detail (str): Подробное сообщение об ошибке.
            extra (Optional[Dict[str, Any]]): Дополнительная информация об ошибке.
        """
        message = detail
        if user_id is not None and group_id is not None:
            message = f"Пользователь с ID {user_id} не состоит в группе с ID {group_id}"

        extra_data = extra or {}
        if user_id is not None:
            extra_data["user_id"] = user_id
        if group_id is not None:
            extra_data["group_id"] = group_id

        super().__init__(
            status_code=400,
            detail=message,
            error_type="user_not_in_group",
            extra=extra_data,
        )
