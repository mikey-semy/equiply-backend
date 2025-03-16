"""
Классы исключений для модуля рабочих пространств.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с рабочими пространствами.

Включают в себя:
- WorkspaceNotFoundError: Исключение, которое вызывается, когда рабочее пространство не найдено.
- WorkspaceMemberNotFoundError: Исключение, которое вызывается, когда участник рабочего пространства не найден.
- WorkspaceAccessDeniedError: Исключение, которое вызывается, когда доступ к рабочему пространству запрещен.
"""

from app.core.exceptions.base import BaseAPIException

class WorkspaceNotFoundError(BaseAPIException):
    """
    Исключение для ненайденного рабочего пространства.

    Возникает, когда запрашиваемое рабочее пространство не найдено в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        workspace_id (int): ID рабочего пространства, которое не найдено.
    """

    def __init__(self, workspace_id: int = None, detail: str = None):
        """
        Инициализирует исключение WorkspaceNotFoundError.

        Args:
            workspace_id (int): ID рабочего пространства, которое не найдено.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Рабочее пространство не найдено"
        if workspace_id is not None:
            message = f"Рабочее пространство с ID={workspace_id} не найдено"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="workspace_not_found",
            extra={"workspace_id": workspace_id} if workspace_id is not None else None
        )


class WorkspaceMemberNotFoundError(BaseAPIException):
    """
    Исключение для ненайденного участника рабочего пространства.

    Возникает, когда запрашиваемый участник рабочего пространства не найден в базе данных.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        workspace_id (int): ID рабочего пространства.
        user_id (int): ID пользователя.
    """

    def __init__(self, workspace_id: int = None, user_id: int = None, detail: str = None):
        """
        Инициализирует исключение WorkspaceMemberNotFoundError.

        Args:
            workspace_id (int): ID рабочего пространства.
            user_id (int): ID пользователя.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Участник рабочего пространства не найден"
        if user_id is not None and workspace_id is not None:
            message = f"Пользователь с ID={user_id} не найден в рабочем пространстве с ID={workspace_id}"

        extra = {}
        if workspace_id is not None:
            extra["workspace_id"] = workspace_id
        if user_id is not None:
            extra["user_id"] = user_id

        super().__init__(
            status_code=404,
            detail=message,
            error_type="workspace_member_not_found",
            extra=extra if extra else None
        )


class WorkspaceAccessDeniedError(BaseAPIException):
    """
    Исключение для отказа в доступе к рабочему пространству.

    Возникает, когда у пользователя недостаточно прав для выполнения операции
    в рабочем пространстве.

    Attributes:
        detail (str): Подробное сообщение об ошибке.
        workspace_id (int): ID рабочего пространства.
        required_role (str): Требуемая роль для выполнения операции.
    """

    def __init__(self, workspace_id: int = None, required_role: str = None, detail: str = None):
        """
        Инициализирует исключение WorkspaceAccessDeniedError.

        Args:
            workspace_id (int): ID рабочего пространства.
            required_role (str): Требуемая роль для выполнения операции.
            detail (str): Подробное сообщение об ошибке.
        """
        message = detail or "Доступ к рабочему пространству запрещен"
        if required_role:
            message = f"Для выполнения этой операции требуется роль {required_role}"

        extra = {}
        if workspace_id is not None:
            extra["workspace_id"] = workspace_id
        if required_role:
            extra["required_role"] = required_role

        super().__init__(
            status_code=403,
            detail=message,
            error_type="workspace_access_denied",
            extra=extra if extra else None
        )

class WorkspaceExistsError(BaseAPIException):
    """
    Исключение для случая, когда рабочее пространство уже существует.

    Возникает при попытке создать рабочее пространство с уже существующим именем.

    Args:
        field: Поле, по которому произошло дублирование.
        value: Значение поля.
    """

    def __init__(self, field: str, value: str):
        """
        Инициализирует исключение WorkspaceExistsError.

        Args:
            field: Поле, по которому произошло дублирование.
            value: Значение поля.
        """
        detail = f"Рабочее пространство с {field} '{value}' уже существует"
        super().__init__(
            status_code=409,
            detail=detail,
            error_type="workspace_already_exists"
        )