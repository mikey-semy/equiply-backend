from typing import Generic, List, TypeVar, Optional, ClassVar, Dict, Type, Any, Literal
from pydantic import BaseModel, Field

from app.schemas.v1.base import CommonBaseSchema

T = TypeVar("T", bound=CommonBaseSchema)

class SortOption(BaseModel):
    """Базовый класс для опций сортировки"""
    field: str
    description: str

class BaseSortFields:
    """Базовый класс для полей сортировки, специфичных для сущностей"""
    CREATED_AT = SortOption(field="created_at", description="Сортировка по дате создания")
    UPDATED_AT = SortOption(field="updated_at", description="Сортировка по дате обновления")
    
    @classmethod
    def get_default(cls) -> SortOption:
        """Возвращает поле сортировки по умолчанию"""
        return cls.UPDATED_AT
    
    @classmethod
    def get_all_fields(cls) -> Dict[str, SortOption]:
        """Возвращает все доступные поля сортировки для этой сущности"""
        return {
            name: value for name, value in cls.__dict__.items() 
            if isinstance(value, SortOption) and not name.startswith('_')
        }
    
    @classmethod
    def get_field_values(cls) -> List[str]:
        """Возвращает список всех значений полей для этой сущности"""
        return [option.field for option in cls.get_all_fields().values()]
    
    @classmethod
    def is_valid_field(cls, field: str) -> bool:
        """Проверяет, является ли поле допустимым для этой сущности"""
        return field in cls.get_field_values()
    
    @classmethod
    def get_field_or_default(cls, field: str) -> str:
        """Возвращает поле, если оно допустимо, иначе возвращает поле по умолчанию"""
        if cls.is_valid_field(field):
            return field
        return cls.get_default().field

class SortFields(BaseSortFields):
    """Стандартные поля сортировки, доступные для всех сущностей"""
    pass

class WorkspaceSortFields(BaseSortFields):
    """Поля сортировки для рабочих пространств"""
    NAME = SortOption(field="name", description="Сортировка по имени рабочего пространства")

class UserSortFields(BaseSortFields):
    """Поля сортировки для пользователей"""
    USERNAME = SortOption(field="username", description="Сортировка по имени пользователя")

class SortFieldRegistry:
    """Реестр классов полей сортировки"""
    _registry: Dict[str, Type[BaseSortFields]] = {
        "Workspace": WorkspaceSortFields,
        "User": UserSortFields,
        "default": SortFields
    }
    
    @classmethod
    def get_sort_field_class(cls, entity_name: str) -> Type[BaseSortFields]:
        """Получает класс полей сортировки для указанной сущности"""
        return cls._registry.get(entity_name, cls._registry["default"])


class Page(BaseModel, Generic[T]):
    """
    Схема для представления страницы результатов запроса.

    Attributes:
        items (List[T]): Список элементов на странице.
        total (int): Общее количество элементов.
        page (int): Номер текущей страницы.
        size (int): Размер страницы.
    """

    items: List[T]
    total: int
    page: int
    size: int


class PaginationParams:
    """
    Параметры для пагинации.

    Attributes:
        skip (int): Количество пропускаемых элементов.
        limit (int): Максимальное количество элементов на странице.
        sort_by (str): Поле для сортировки.
        sort_desc (bool): Флаг сортировки по убыванию.
    """

    def __init__(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "updated_at",
        sort_desc: bool = True,
        entity_name: str = "default"
    ):
        self.skip = skip
        self.limit = limit
        
        # Получаем соответствующий класс полей сортировки для сущности
        sort_field_class = SortFieldRegistry.get_sort_field_class(entity_name)
        
        # Проверяем и устанавливаем поле сортировки
        self.sort_by = sort_field_class.get_field_or_default(sort_by)
        self.sort_desc = sort_desc

    @property
    def page(self) -> int:
        """
        Получает номер текущей страницы.

        Returns:
            int: Номер текущей страницы.

        """
        return self.skip // self.limit + 1
