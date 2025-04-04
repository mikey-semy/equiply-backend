from typing import Generic, List, TypeVar, Optional, ClassVar, Dict, Type, Any, Literal
from pydantic import BaseModel, Field

from app.schemas.v1.base import CommonBaseSchema

T = TypeVar("T", bound=CommonBaseSchema)

class SortOption(BaseModel):
    """
    Базовый класс для опций сортировки.
    
    Представляет отдельное поле сортировки с его идентификатором и описанием.
    
    Attributes:
        field (str): Идентификатор поля для использования в запросах сортировки.
        description (str): Человекочитаемое описание поля сортировки.
    """
    field: str
    description: str

class BaseSortFields:
    """
    Базовый класс для полей сортировки, специфичных для сущностей.
    
    Определяет стандартные поля сортировки (created_at, updated_at) и методы
    для работы с полями сортировки.
    
    Attributes:
        CREATED_AT (SortOption): Поле сортировки по дате создания.
        UPDATED_AT (SortOption): Поле сортировки по дате обновления.
    """
    CREATED_AT = SortOption(field="created_at", description="Сортировка по дате создания")
    UPDATED_AT = SortOption(field="updated_at", description="Сортировка по дате обновления")
    
    @classmethod
    def get_default(cls) -> SortOption:
        """
        Возвращает поле сортировки по умолчанию.
        
        По умолчанию используется сортировка по дате обновления (UPDATED_AT).
        
        Returns:
            SortOption: Опция сортировки, используемая по умолчанию.
        
        Usage:
            default_option = BaseSortFields.get_default()
            default_field = default_option.field  # "updated_at"
        """
        return cls.UPDATED_AT
    
    @classmethod
    def get_all_fields(cls) -> Dict[str, SortOption]:
        """
        Возвращает все доступные поля сортировки для этой сущности.
        
        Метод собирает все атрибуты класса, которые являются экземплярами SortOption
        и не начинаются с подчеркивания.
        
        Returns:
            Dict[str, SortOption]: Словарь, где ключи - имена полей, а значения - экземпляры SortOption.
        
        Usage:
            fields = BaseSortFields.get_all_fields()
            # {'CREATED_AT': SortOption(field='created_at', description='...'), ...}
        """
        return {
            name: value for name, value in cls.__dict__.items() 
            if isinstance(value, SortOption) and not name.startswith('_')
        }
    
    @classmethod
    def get_field_values(cls) -> List[str]:
        """
        Возвращает список всех значений полей для этой сущности.
        
        Извлекает значения поля field из всех доступных опций сортировки.
        
        Returns:
            List[str]: Список строковых идентификаторов полей сортировки.
        
        Usage:
            values = BaseSortFields.get_field_values()
            # ['created_at', 'updated_at']
        """
        return [option.field for option in cls.get_all_fields().values()]
    
    @classmethod
    def is_valid_field(cls, field: str) -> bool:
        """
        Проверяет, является ли поле допустимым для этой сущности.
        
        Args:
            field (str): Идентификатор поля для проверки.
        
        Returns:
            bool: True, если поле допустимо, иначе False.
        
        Usage:
            if BaseSortFields.is_valid_field('created_at'):
                # Поле допустимо
            else:
                # Поле недопустимо
        """
        return field in cls.get_field_values()
    
    @classmethod
    def get_field_or_default(cls, field: str) -> str:
        """
        Возвращает поле, если оно допустимо, иначе возвращает поле по умолчанию.
        
        Проверяет допустимость указанного поля и возвращает его, если оно допустимо.
        В противном случае возвращает поле по умолчанию.
        
        Args:
            field (str): Идентификатор поля для проверки.
        
        Returns:
            str: Идентификатор допустимого поля сортировки.
        
        Usage:
            sort_field = BaseSortFields.get_field_or_default('invalid_field')
            # Вернет 'updated_at', так как 'invalid_field' недопустимо
        """
        if cls.is_valid_field(field):
            return field
        return cls.get_default().field

class SortFields(BaseSortFields):
    """
    Стандартные поля сортировки, доступные для всех сущностей.
    
    Наследует базовые поля сортировки (created_at, updated_at) без добавления новых.
    Используется как класс по умолчанию, когда специфичный класс не найден.
    
    Usage:
        fields = SortFields.get_field_values()  # ['created_at', 'updated_at']
    """
    pass

class WorkspaceSortFields(BaseSortFields):
    """
    Поля сортировки для рабочих пространств.
    
    Расширяет базовые поля сортировки, добавляя специфичные для рабочих пространств
    поля, такие как имя.
    
    Attributes:
        NAME (SortOption): Поле сортировки по имени рабочего пространства.
    
    Usage:
        fields = WorkspaceSortFields.get_field_values()  
        # ['name', 'created_at', 'updated_at']
    """
    NAME = SortOption(field="name", description="Сортировка по имени рабочего пространства")

class UserSortFields(BaseSortFields):
    """
    Поля сортировки для пользователей.
    
    Расширяет базовые поля сортировки, добавляя специфичные для пользователей
    поля, такие как имя пользователя.
    
    Attributes:
        USERNAME (SortOption): Поле сортировки по имени пользователя.
    
    Usage:
        fields = UserSortFields.get_field_values()  
        # ['username', 'created_at', 'updated_at']
    """
    USERNAME = SortOption(field="username", description="Сортировка по имени пользователя")

class SortFieldRegistry:
    """
    Реестр классов полей сортировки.
    
    Предоставляет централизованный доступ к классам полей сортировки для различных
    типов сущностей. Позволяет получить соответствующий класс по имени сущности.
    
    Attributes:
        _registry (Dict[str, Type[BaseSortFields]]): Словарь, сопоставляющий имена 
            сущностей с соответствующими классами полей сортировки.
    """
    _registry: Dict[str, Type[BaseSortFields]] = {
        "Workspace": WorkspaceSortFields,
        "User": UserSortFields,
        "default": SortFields
    }
    
    @classmethod
    def get_sort_field_class(cls, entity_name: str) -> Type[BaseSortFields]:
        """
        Получает класс полей сортировки для указанной сущности.
        
        Возвращает соответствующий класс полей сортировки по имени сущности.
        Если класс для указанной сущности не найден, возвращает класс по умолчанию.
        
        Args:
            entity_name (str): Имя сущности, для которой требуется получить класс полей сортировки.
        
        Returns:
            Type[BaseSortFields]: Класс полей сортировки для указанной сущности.
        
        Usage:
            # Получение класса полей сортировки для рабочих пространств
            workspace_sort_fields = SortFieldRegistry.get_sort_field_class("Workspace")
            
            # Получение класса полей сортировки для несуществующей сущности
            # (вернет SortFields)
            default_sort_fields = SortFieldRegistry.get_sort_field_class("NonExistent")
        """
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
