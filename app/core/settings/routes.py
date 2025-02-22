from typing import List, Dict, Any

class RouteConfig:
    """
    Конфигурация эндпоинтов.

    Attributes:
        prefix (str): Префикс URL для группы эндпоинтов
        tags (List[str]): Список тегов для Swagger документации

    Example:
        >>> route = RouteConfig("users", ["Users API"])
        >>> route.to_dict()
        {'prefix': '/users', 'tags': ['Users API']}
    """

    def __init__(self, prefix: str, tags: List[str]):
        """
        Args:
            prefix: Префикс URL без начального слеша
            tags: Список тегов для группировки эндпоинтов
        """
        self.prefix = f"/{prefix}" if prefix else ""
        self.tags = tags

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует конфигурацию в словарь для FastAPI router.

        Returns:
            Dict с prefix и tags для настройки APIRouter
        """
        return {"prefix": self.prefix, "tags": self.tags}