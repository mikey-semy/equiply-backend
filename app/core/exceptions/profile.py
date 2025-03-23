from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class ProfileNotFoundError(BaseAPIException):
    """
    Профиль пользователя не найден.

    Attributes:
        detail (str): Подробности об ошибке.
        extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
    """

    def __init__(
        self, detail: str = "Профиль не найден", extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=404, detail=detail, error_type="profile_not_found", extra=extra
        )


class InvalidFileTypeError(BaseAPIException):
    """
    Неверный тип файла.

    Attributes:
        detail (str): Подробности об ошибке.
        extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
    """

    def __init__(
        self,
        detail: str = "Неверный тип файла. Поддерживаются только JPEG и PNG",
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=415, detail=detail, error_type="invalid_file_type", extra=extra
        )


class FileTooLargeError(BaseAPIException):
    """
    Размер файла превышает допустимый лимит.

    Attributes:
        detail (str): Подробности об ошибке.
        extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
    """

    def __init__(
        self,
        detail: str = "Размер файла превышает допустимый лимит (2MB)",
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=413, detail=detail, error_type="file_too_large", extra=extra
        )


class StorageError(BaseAPIException):
    """
    Ошибка при работе с хранилищем файлов.

    Attributes:
        detail (str): Подробности об ошибке.
        extra (Optional[Dict[str, Any]]): Дополнительные данные об ошибке.
    """

    def __init__(
        self,
        detail: str = "Ошибка при загрузке файла в хранилище",
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=500, detail=detail, error_type="storage_error", extra=extra
        )
