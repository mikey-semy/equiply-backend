from typing import List, Optional, Dict, Any, Type
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
    def create_error_responses(*exception_classes: Type[Exception]) -> Dict[int, Dict[str, Any]]:
        """
        Создает словарь с ответами об ошибках для документации FastAPI.

        Args:
            *exception_classes: Классы исключений

        Returns:
            Словарь вида {status_code: {"model": ErrorResponseSchema, "description": ...}}

        Пример использования:
            @self.router.get(
                "",
                response_model=UserResponseSchema,
                responses=self.create_error_responses(
                    InvalidCredentialsError,
                    UserNotFoundError
                )
            )
            async def get_user(): ...
        """
        responses = {}

        for exc_class in exception_classes:
            # Определяем код статуса на основе имени или атрибута класса
            status_code = getattr(exc_class, "status_code", 500)

            # Получаем описание из документации класса
            description = exc_class.__doc__ or exc_class.__name__

            # Если статус-код уже есть, объединяем описания
            if status_code in responses:
                responses[status_code]["description"] += f", {description.strip()}"
            else:
                responses[status_code] = {
                    "model": ErrorResponseSchema,
                    "description": description.strip(),
                }

        return responses