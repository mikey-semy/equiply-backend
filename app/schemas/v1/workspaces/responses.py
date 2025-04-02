"""
Схемы ответов для модуля рабочих пространств.
"""

from typing import List

from app.schemas.v1.base import BaseResponseSchema
from app.schemas.v1.pagination import Page
from app.schemas.v1.workspaces.base import (WorkspaceDataSchema,
                                            WorkspaceDetailDataSchema,
                                            WorkspaceMemberDataSchema)


class WorkspaceResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
        data (WorkspaceDataSchema): Данные рабочего пространства
    """

    message: str = "Рабочее пространство успешно получено"
    data: WorkspaceDataSchema


class WorkspaceDetailResponseSchema(BaseResponseSchema):
    """
    Схема ответа с детальными данными рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
        data (WorkspaceDetailDataSchema): Детальные данные рабочего пространства
    """

    message: str = "Детальная информация о рабочем пространстве успешно получена"
    data: WorkspaceDetailDataSchema


class WorkspaceListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком рабочих пространств.

    Attributes:
        message (str): Сообщение о результате операции
        data (Page[WorkspaceDataSchema]): Список данных рабочих пространств
    """

    message: str = "Список рабочих пространств успешно получен"
    data: Page[WorkspaceDataSchema]


class WorkspaceCreateResponseSchema(WorkspaceResponseSchema):
    """
    Схема ответа при создании рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
        data (WorkspaceDataSchema): Данные созданного рабочего пространства
    """

    message: str = "Рабочее пространство успешно создано"


class WorkspaceUpdateResponseSchema(WorkspaceResponseSchema):
    """
    Схема ответа при обновлении рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
        data (WorkspaceDataSchema): Данные обновленного рабочего пространства
    """

    message: str = "Рабочее пространство успешно обновлено"


class WorkspaceDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Рабочее пространство успешно удалено"


class WorkspaceMemberResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными участника рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
        data (WorkspaceMemberDataSchema): Данные участника рабочего пространства
    """

    message: str = "Информация об участнике рабочего пространства успешно получена"
    data: WorkspaceMemberDataSchema


class WorkspaceMemberListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком участников рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
        data (Page[WorkspaceMemberDataSchema]): Список данных участников рабочего пространства
        total (int): Общее количество участников
    """

    message: str = "Список участников рабочего пространства успешно получен"
    data: Page[WorkspaceMemberDataSchema]


class WorkspaceMemberAddResponseSchema(WorkspaceMemberResponseSchema):
    """
    Схема ответа при добавлении участника в рабочее пространство.

    Attributes:
        message (str): Сообщение о результате операции
        data (WorkspaceMemberDataSchema): Данные добавленного участника
    """

    message: str = "Участник успешно добавлен в рабочее пространство"


class WorkspaceMemberUpdateResponseSchema(WorkspaceMemberResponseSchema):
    """
    Схема ответа при обновлении роли участника рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
        data (WorkspaceMemberDataSchema): Данные участника с обновленной ролью
    """

    message: str = "Роль участника рабочего пространства успешно обновлена"


class WorkspaceMemberRemoveResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении участника из рабочего пространства.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Участник успешно удален из рабочего пространства"
