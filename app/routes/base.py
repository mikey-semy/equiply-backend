from typing import Optional, Sequence

from fastapi import APIRouter


class BaseRouter:
    """
    Базовый класс для всех роутеров.

    Предоставляет общий функционал для создания обычных и защищенных маршрутов.
    Защищенные маршруты автоматически обновляют время последней активности пользователя.

    Attributes:
        router (APIRouter): Базовый FastAPI роутер
    """

    def __init__(self, prefix: str = "", tags: Optional[Sequence[str]] = None):
        """
        Инициализирует базовый роутер.

        Args:
            prefix (str): Префикс URL для всех маршрутов
            tags (List[str]): Список тегов для документации Swagger
        """
        self.router = APIRouter(prefix=f"/{prefix}" if prefix else "", tags=tags or [])
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
