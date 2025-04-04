from typing import Generic, List, TypeVar, Optional, ClassVar, Dict, Type
from enum import Enum
from pydantic import BaseModel

from app.schemas.v1.base import CommonBaseSchema

T = TypeVar("T", bound=CommonBaseSchema)

class BaseSortField(str, Enum):
    """ 
    Базовый класс для полей сортировки. 
    Все специфичные для сущностей классы сортировки должны наследоваться от этого класса.

    Usage:

    1. Создать специфичный класс со своими (существующими) полями сортировки:

        class WorkspaceSortField(BaseSortField): 
            NAME = "name"

    2. Применить класс со значением по умолчанию:
        sort_by: WorkspaceSortField = Query(
            WorkspaceSortField.UPDATED_AT, (??? .value нужен ???)
            description=f"Поле для сортировки ({', '.join([field.value for field in WorkspaceSortField])})"
        ), 
    """
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

    _registry: ClassVar[Dict[str, Type["BaseSortField"]]] = {} # Словарь для хранения зарегистрированных классов сортировки
    _default_field: ClassVar[str] = "UPDATED_AT" # Поле по умолчанию для сортировки

    def __init_subclass__(cls, **kwargs):
        """
        Регистрирует подклассы в реестре.
        """
        super().__init_subclass__(**kwargs)
        cls._registry[cls.__name__] = cls

    @classmethod
    def get_default(cls) -> "SortField":
        """Возвращает поле сортировки по умолчанию."""
        return cls.UPDATED_AT

    @classmethod
    def _missing_(cls, value: str) -> Optional["SortField"]:
        """Обрабатывает случай, когда значение не найдено в enum."""
        return cls.get_default()

    @classmethod
    def get_sort_field_class(cls, entity_name: str) -> Type["BaseSortField"]:
        """
        Получает класс полей сортировки для указанной сущности.

        Args:
            entity_name: Имя сущности (например, 'Workspace', 'User')

        Returns:
            Класс полей сортировки для указанной сущности или базовый класс, если специфичный не найден
        """
        class_name = f"{entity_name}SortField"
        return cls._registry.get(class_name, cls)

class SortField(BaseSortField): 
    """ Стандартные поля для сортировки, доступные для всех сущностей. """ 
    pass

class WorkspaceSortField(BaseSortField): 
    """ 
    Поля для сортировки рабочих пространств. 
    """ 
    NAME = "name"

class UserSortField(BaseSortField): 
    """ 
    Поля для сортировки пользователей. 
    """ 
    USERNAME = "username" 


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
    ):
        self.skip = skip
        self.limit = limit
        self.sort_by = sort_by
        self.sort_desc = sort_desc

    @property
    def page(self) -> int:
        """
        Получает номер текущей страницы.

        Returns:
            int: Номер текущей страницы.

        """
        return self.skip // self.limit + 1
