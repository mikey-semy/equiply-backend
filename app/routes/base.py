from typing import List, Optional, Dict, Any, Type, Union
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter
from app.schemas import ErrorResponseSchema

class BaseRouter:
    """
    Базовый класс для всех роутеров.

    Предоставляет общий функционал для создания обычных и защищенных маршрутов.
    Защищенные маршруты автоматически обновляют время последней активности пользователя.

    Attributes:
        router (APIRouter): Базовый FastAPI роутер
    """
    def __init__(
            self,
            prefix: str = "",
            tags: Optional[List[str]] = None
    ):
        """
        Инициализирует базовый роутер.

        Args:
            prefix (str): Префикс URL для всех маршрутов
            tags (List[str]): Список тегов для документации Swagger
        """
        self.router = APIRouter(
            prefix=f"/{prefix}" if prefix else "",
            tags=tags or []
        )
        self.configure()

    def configure(self):
        """Переопределяется в дочерних классах для настройки роутов"""
        pass

    def get_router(self) -> APIRouter:
        """
        Возвращает настроенный FastAPI роутер.

        Returns:
            APIRouter: Настроенный FastAPI роутер
        """
        return self.router

    @staticmethod
    def create_error_responses(*exception_classes: Union[Type[Exception], int],
                              include_auth_error: bool = True) -> Dict[int, Dict[str, Any]]:
        """
        Создает словарь с ответами об ошибках для документации FastAPI.

        Args:
            *exception_classes: Классы исключений или статус-коды
            include_auth_error: Добавить ли стандартную ошибку аутентификации 401

        Returns:
            Словарь с описанием ошибок для OpenAPI

        Пример использования:
            @self.router.get(
                "",
                response_model=UserResponseSchema,
                responses=self.create_error_responses(
                    ProfileNotFoundError,      # Автоматически добавит 401 и указанную ошибку с кодом 404
                    include_auth_error=False,  # Не добавлять стандартную ошибку 401
                    422  # Добавит стандартную ошибку 422 (Unprocessable Entity)
                )
            )
        """
        responses = {}

        # Добавляем стандартную ошибку аутентификации, если запрошено
        if include_auth_error:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            request_id = str(uuid.uuid4())

            responses[401] = {
                "model": ErrorResponseSchema,
                "description": "Ошибка авторизации",
                "content": {
                    "application/json": {
                        "example": {
                            "success": False,
                            "message": None,
                            "data": None,
                            "error": {
                                "detail": "Not authenticated",
                                "error_type": "http_error",
                                "status_code": 401,
                                "timestamp": timestamp,
                                "request_id": request_id,
                                "extra": None
                            }
                        }
                    }
                }
            }

        # Обрабатываем предоставленные исключения
        for exc in exception_classes:
            if isinstance(exc, int):
                # Если передан статус-код напрямую
                status_code = exc
                error_type = f"http_{status_code}"
                detail = f"HTTP Error {status_code}"
            else:
                # Если передан класс исключения
                status_code = getattr(exc, "status_code", 500)
                error_type = getattr(exc, "default_error_type", exc.__name__.lower())
                detail = exc.__doc__.strip() if exc.__doc__ else exc.__name__

            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            request_id = str(uuid.uuid4())

            responses[status_code] = {
                "model": ErrorResponseSchema,
                "description": detail,
                "content": {
                    "application/json": {
                        "example": {
                            "success": False,
                            "message": None,
                            "data": None,
                            "error": {
                                "detail": detail,
                                "error_type": error_type,
                                "status_code": status_code,
                                "timestamp": timestamp,
                                "request_id": request_id,
                                "extra": None
                            }
                        }
                    }
                }
            }

        return responses