"""
Исключения для аутентификации и управления пользователями.

1. Базовый класс AuthenticationError наследуется от BaseAPIException

2. Специфические исключения наследуются от AuthenticationError:
- InvalidCredentialsError - неверные учетные данные
- InvalidEmailFormatError - неверный формат email
- InvalidPasswordError - неверный пароль
- WeakPasswordError - слабый пароль

3. Отдельная ветка для работы с токенами:
- TokenError - базовый класс ошибок токена
- TokenMissingError - отсутствующий токен
- TokenExpiredError - истекший токен
"""

from app.core.exceptions.base import BaseAPIException


class AuthenticationError(BaseAPIException):
    """
    Базовый класс ошибок аутентификации
    """

    def __init__(
        self,
        detail: str = "Ошибка аутентификации",
        error_type: str = "authentication_error",
        extra: dict = None,
    ):
        super().__init__(
            status_code=401, detail=detail, error_type=error_type, extra=extra or {}
        )


class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные"""

    def __init__(self):
        super().__init__(
            detail="🔐 Неверный email или пароль",
            error_type="invalid_credentials",
        )


class InvalidEmailFormatError(AuthenticationError):
    """
    Исключение, которое вызывается, когда формат email недействителен.

    Attributes:
        email (str): Недействительный email.
    """

    def __init__(self, email: str):
        super().__init__(
            detail=f"Неверный формат email: {email}",
            error_type="invalid_email_format",
            extra={"email": email}
        )


class InvalidPasswordError(AuthenticationError):
    """
    Исключение при неверном пароле во время входа
    """

    def __init__(self):
        super().__init__(
            detail="Неверный пароль",
            error_type="invalid_password",
        )


class WeakPasswordError(AuthenticationError):
    """
    Исключение, которое вызывается, когда пароль является слабым.
    """

    def __init__(self):
        super().__init__(
            detail="Пароль должен быть минимум 8 символов!",
            error_type="weak_password",
        )


class TokenError(AuthenticationError):
    """Базовая ошибка токена"""

    def __init__(
        self, detail: str, error_type: str = "token_error", extra: dict = None
    ):
        super().__init__(
            detail=detail, error_type=error_type, extra=extra or {"token": True}
        )


class TokenMissingError(TokenError):
    """Токен отсутствует"""

    def __init__(self):
        super().__init__(detail="Токен отсутствует", error_type="token_missing")


class TokenExpiredError(TokenError):
    """Токен просрочен"""

    def __init__(self):
        super().__init__(detail="Токен просрочен", error_type="token_expired")


class TokenInvalidError(TokenError):
    """Невалидный токен"""

    def __init__(self):
        super().__init__(detail="Невалидный токен", error_type="token_invalid")
