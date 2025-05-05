"""
Модуль схем ответов для групп пользователей.
"""

from typing import List

from app.schemas.v1.base import BaseResponseSchema
from app.schemas.v1.groups.base import UserGroupSchema, UserGroupMemberSchema
from app.schemas.v1.pagination import Page


class UserGroupResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными группы пользователей.

    Attributes:
        message (str): Сообщение об успешном получении группы.
        data (UserGroupSchema): Данные группы пользователей.
    """
    message: str = "Группа пользователей успешно получена"
    data: UserGroupSchema


class UserGroupListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком групп пользователей.

    Attributes:
        message (str): Сообщение об успешном получении списка групп.
        data (Page[UserGroupSchema]): Страница с группами пользователей.
    """
    message: str = "Список групп пользователей успешно получен"
    data: Page[UserGroupSchema]


class UserGroupCreateResponseSchema(UserGroupResponseSchema):
    """
    Схема ответа при создании группы пользователей.

    Attributes:
        message (str): Сообщение об успешном создании группы.
        data (UserGroupSchema): Данные созданной группы пользователей.
    """
    message: str = "Группа пользователей успешно создана"


class UserGroupUpdateResponseSchema(UserGroupResponseSchema):
    """
    Схема ответа при обновлении группы пользователей.

    Attributes:
        message (str): Сообщение об успешном обновлении группы.
        data (UserGroupSchema): Данные обновленной группы пользователей.
    """
    message: str = "Группа пользователей успешно обновлена"


class UserGroupDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении группы пользователей.

    Attributes:
        message (str): Сообщение об успешном удалении группы.
    """
    message: str = "Группа пользователей успешно удалена"


class UserGroupMemberResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными члена группы.

    Attributes:
        message (str): Сообщение об успешном добавлении пользователя в группу.
        data (UserGroupMemberSchema): Данные о членстве пользователя в группе.
    """
    message: str = "Пользователь успешно добавлен в группу"
    data: UserGroupMemberSchema


class UserGroupMembersResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком членов группы.

    Attributes:
        message (str): Сообщение об успешном получении списка членов группы.
        data (List[UserGroupMemberSchema]): Список членов группы.
    """
    message: str = "Список членов группы успешно получен"
    data: List[UserGroupMemberSchema]
