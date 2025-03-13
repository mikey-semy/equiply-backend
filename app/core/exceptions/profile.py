from app.core.exceptions.base import BaseAPIException

class ProfileNotFoundError(BaseAPIException):
    """
    Профиль пользователя не найден.

    Attributes:
        detail (str): Подробности об ошибке.
        extra (dict): Дополнительные данные об ошибке.
    """

    def __init__(self, detail: str = "Профиль не найден", extra: dict = None):
        super().__init__(
            status_code=404,
            detail=detail,
            error_type="profile_not_found",
            extra=extra
        )
