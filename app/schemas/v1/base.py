"""
Модуль для определения базовой схемы данных.

Этот модуль содержит класс `CommonBaseSchema`, который наследуется от
`BaseModel` библиотеки Pydantic. Класс предназначен для использования
в других схемах и предоставляет общую конфигурацию для валидации
и сериализации данных.

Класс `BaseSchema` включает в себя настройки, которые позволяют
использовать атрибуты модели в качестве полей схемы.

Класс `BaseRequestSchema` - если в использоовании общих атрибутов
из BaseSchema нет необходимости или они будут другие
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar, Dict, Any

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class CommonBaseSchema(BaseModel):
    """
    Общая базовая схема для всех моделей.
    Содержит только общую конфигурацию и метод to_dict().

    Attributes:
        model_config (ConfigDict): Конфигурация модели, позволяющая
        использовать атрибуты в качестве полей.

    Methods:
        to_dict(): Преобразует объект в словарь.
    """

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self) -> dict:
        return self.model_dump()


class BaseSchema(CommonBaseSchema):
    """
    Базовая схема для всех моделей данных.

    Этот класс наследуется от `CommonBaseSchema` и предоставляет общую
    конфигурацию для всех схем, включая возможность использования
    атрибутов модели в качестве полей схемы.

    Attributes:
        id (int): Идентификатор записи.
        created_at (datetime): Дата и время создания записи.
        updated_at (datetime): Дата и время последнего обновления записи.
    """

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BaseRequestSchema(CommonBaseSchema):
    """
    Базовая схема для входных данных.
    Этот класс наследуется от `CommonBaseSchema`
    и предоставляет общую конфигурацию для всех схем входных данных.

    Так как нету необходимости для ввода исходных данных id и даты создания и обновления.
    """

    pass


class BaseResponseSchema(CommonBaseSchema):
    """
    Базовая схема для ответов API.

    Этот класс наследуется от `CommonBaseSchema` и предоставляет общую
    конфигурацию для всех схем ответов, включая возможность добавления
    метаданных и сообщений об ошибках.

    Attributes:
        success (bool): Указывает, успешен ли запрос.
        message (Optional[str]): Сообщение, связанное с ответом.
    """

    success: bool = True
    message: Optional[str] = None


class ErrorSchema(CommonBaseSchema):
    """
    Схема для представления данных об ошибке.

    Attributes:
        detail: Подробное описание ошибки
        error_type: Тип ошибки для идентификации на клиенте
        status_code: HTTP код ответа
        timestamp: Временная метка возникновения ошибки
        request_id: Уникальный идентификатор запроса
        extra: Дополнительные данные об ошибке
    """

    detail: str
    error_type: str
    status_code: int
    timestamp: str
    request_id: str
    extra: Optional[Dict[str, Any]] = None


class ErrorResponseSchema(BaseResponseSchema):
    """
    Модель для представления API ошибок в документации.

    Соответствует формату исключений, обрабатываемых в handlers.py.
    Обеспечивает единый формат ответов с ошибками во всем API.

    Attributes:
        success: Всегда False для ошибок
        message: Информационное сообщение, обычно None для ошибок
        data: Всегда None для ошибок
        error: Детальная информация об ошибке
    """

    success: bool = False
    message: Optional[str] = None
    data: None = None
    error: ErrorSchema


class ItemResponseSchema(BaseResponseSchema, Generic[T]):
    """
    Схема для ответов, содержащих один элемент.

    Attributes:
        item (T): Элемент, возвращаемый в ответе.
    """

    item: T


class ListResponseSchema(BaseResponseSchema, Generic[T]):
    """
    Схема для ответов, содержащих список элементов.

    Attributes:
        items (List[T]): Список элементов, возвращаемых в ответе.
    """

    items: List[T]


class MetaResponseSchema(BaseResponseSchema):
    """
    Схема для ответов с метаданными.

    Attributes:
        meta (dict): Метаданные, связанные с ответом.
    """

    meta: dict
