from app.core.exceptions.base import BaseAPIException


class AIError(BaseAPIException):
    def __init__(
        self, message: str, error_type: str, status_code: int = 400, extra: dict = None
    ):
        super().__init__(
            status_code=status_code, detail=message, error_type=error_type, extra=extra
        )


class AICompletionError(AIError):
    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка при получении ответа от AI: {message}",
            error_type="ai_completion_error",
            status_code=500,
            extra=extra,
        )


class AIConfigError(AIError):
    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка конфигурации AI: {message}",
            error_type="ai_config_error",
            status_code=500,
            extra=extra,
        )


class AIAuthError(AIError):
    def __init__(self, message: str = "Ошибка авторизации в API"):
        super().__init__(message=message, error_type="ai_auth_error", status_code=401)
