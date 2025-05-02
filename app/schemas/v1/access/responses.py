"""Схемы ответов для модуля контроля доступа."""

from typing import List

from app.schemas.v1.access import (AccessPolicySchema, AccessRuleSchema,
                                   UserAccessSettingsSchema)
from app.schemas.v1.base import BaseResponseSchema
from app.schemas.v1.pagination import Page

from .base import PermissionCheckDataSchema


class AccessPolicyResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными политики доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (AccessPolicySchema): Данные политики доступа
    """

    message: str = "Политика доступа успешно получена"
    data: AccessPolicySchema


class AccessPolicyListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком политик доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (Page[AccessPolicySchema]): Страница со списком политик доступа
    """

    message: str = "Список политик доступа успешно получен"
    data: Page[AccessPolicySchema]


class AccessPolicyCreateResponseSchema(AccessPolicyResponseSchema):
    """
    Схема ответа при создании политики доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (AccessPolicySchema): Данные созданной политики доступа
    """

    message: str = "Политика доступа успешно создана"


class AccessPolicyUpdateResponseSchema(AccessPolicyResponseSchema):
    """
    Схема ответа при обновлении политики доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (AccessPolicySchema): Данные обновленной политики доступа
    """

    message: str = "Политика доступа успешно обновлена"


class AccessPolicyDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении политики доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (Optional): Всегда None для операции удаления
    """

    message: str = "Политика доступа успешно удалена"


class AccessRuleResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными правила доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (AccessRuleSchema): Данные правила доступа
    """

    message: str = "Правило доступа успешно получено"
    data: AccessRuleSchema


class AccessRuleListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком правил доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (Page[AccessRuleSchema]): Страница со списком правил доступа
    """

    message: str = "Список правил доступа успешно получен"
    data: Page[AccessRuleSchema]


class AccessRuleCreateResponseSchema(AccessRuleResponseSchema):
    """
    Схема ответа при создании правила доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (AccessRuleSchema): Данные созданного правила доступа
    """

    message: str = "Правило доступа успешно создано"


class AccessRuleUpdateResponseSchema(AccessRuleResponseSchema):
    """
    Схема ответа при обновлении правила доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (AccessRuleSchema): Данные обновленного правила доступа
    """

    message: str = "Правило доступа успешно обновлено"


class AccessRuleDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении правила доступа.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (Optional): Всегда None для операции удаления
    """

    message: str = "Правило доступа успешно удалено"


class UserPermissionsResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком разрешений пользователя для ресурса.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (UserPermissionsDataSchema): Данные о разрешениях пользователя
    """

    message: str = "Список разрешений пользователя успешно получен"
    data: List[str]


class UserAccessSettingsResponseSchema(BaseResponseSchema):
    """
    Схема ответа с настройками доступа пользователя.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (UserAccessSettingsSchema): Данные настроек доступа пользователя
    """

    message: str = "Настройки доступа пользователя успешно получены"
    data: UserAccessSettingsSchema


class PermissionCheckResponseSchema(BaseResponseSchema):
    """
    Схема ответа на запрос проверки разрешения.

    Attributes:
        success (bool): Указывает, успешен ли запрос (наследуется от BaseResponseSchema)
        message (str): Сообщение о результате операции
        data (PermissionCheckDataSchema): Результат проверки разрешения
    """

    message: str = "Проверка разрешения выполнена успешно"
    data: PermissionCheckDataSchema
