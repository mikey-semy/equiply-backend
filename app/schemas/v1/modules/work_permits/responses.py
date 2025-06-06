from typing import List

from app.schemas.v1.base import BaseResponseSchema
from app.schemas.v1.pagination import Page

from .base import (
    WorkPermitSchema,
    WorkPermitDetailSchema,
    SubdivisionSchema,
    ProfessionSchema,
    UserForSelectionSchema
)


class WorkPermitResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными наряда-допуска.

    Используется для возврата информации о конкретном наряде-допуске
    при запросе его детальных данных.

    Attributes:
        message: Сообщение о результате операции
        data: Детальная информация о наряде-допуске
    """
    message: str = "Наряд-допуск успешно получен"
    data: WorkPermitDetailSchema


class WorkPermitCreateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при создании наряда-допуска.

    Возвращается после успешного создания нового наряда-допуска
    с полной информацией о созданном документе.

    Attributes:
        message: Сообщение об успешном создании
        data: Данные созданного наряда-допуска
    """
    message: str = "Наряд-допуск успешно создан"
    data: WorkPermitDetailSchema


class WorkPermitUpdateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при обновлении наряда-допуска.

    Возвращается после успешного обновления существующего наряда-допуска
    с актуальной информацией о документе.

    Attributes:
        message: Сообщение об успешном обновлении
        data: Обновленные данные наряда-допуска
    """
    message: str = "Наряд-допуск успешно обновлен"
    data: WorkPermitDetailSchema


class WorkPermitDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении наряда-допуска.

    Возвращается после успешного удаления наряда-допуска
    без дополнительных данных.

    Attributes:
        message: Сообщение об успешном удалении
    """
    message: str = "Наряд-допуск успешно удален"


class WorkPermitListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком нарядов-допусков.

    Используется для возврата постраничного списка нарядов-допусков
    с возможностью фильтрации и сортировки.

    Attributes:
        message: Сообщение о результате операции
        data: Страница со списком нарядов-допусков
    """
    message: str = "Список нарядов-допусков успешно получен"
    data: Page[WorkPermitSchema]


class SubdivisionListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком подразделений.

    Возвращает полный список активных подразделений организации
    для использования в справочниках и формах выбора.

    Attributes:
        message: Сообщение о результате операции
        data: Список подразделений
    """
    message: str = "Список подразделений успешно получен"
    data: List[SubdivisionSchema]


class ProfessionListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком профессий.

    Возвращает полный список активных профессий и должностей
    для использования в справочниках и классификации персонала.

    Attributes:
        message: Сообщение о результате операции
        data: Список профессий
    """
    message: str = "Список профессий успешно получен"
    data: List[ProfessionSchema]


class UsersForSelectionResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком пользователей для выбора.

    Возвращает постраничный список пользователей с информацией,
    необходимой для выбора участников наряда-допуска.

    Attributes:
        message: Сообщение о результате операции
        data: Страница со списком пользователей
    """
    message: str = "Список пользователей для выбора успешно получен"
    data: Page[UserForSelectionSchema]
