"""Схемы ответов для модуля контроля доступа."""

from typing import List

from app.schemas.v1.access import (AccessPolicySchema, AccessRuleSchema,
                                   UserAccessSettingsSchema)
from app.schemas.v1.base import BaseResponseSchema
from app.schemas.v1.pagination import Page


class AccessPolicyResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными политики доступа.

    Attributes:
        message (str): Сообщение о результате операции
        data (AccessPolicySchema): Данные политики доступа
    """

    message: str = "Политика доступа успешно получена"
    data: AccessPolicySchema


class AccessPolicyListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком политик доступа.

    Attributes:
        message (str): Сообщение о результате операции
        data (Page[AccessPolicySchema]): Список политик доступа
    """

    message: str = "Список политик доступа успешно получен"
    data: Page[AccessPolicySchema]


class AccessPolicyCreateResponseSchema(AccessPolicyResponseSchema):
    """
    Схема ответа при создании политики доступа.

    Attributes:
        message (str): Сообщение о результате операции
        data (AccessPolicySchema): Данные созданной политики доступа
    """

    message: str = "Политика доступа успешно создана"


class AccessPolicyUpdateResponseSchema(AccessPolicyResponseSchema):
    """
    Схема ответа при обновлении политики доступа.

    Attributes:
        message (str): Сообщение о результате операции
        data (AccessPolicySchema): Данные обновленной политики доступа
    """

    message: str = "Политика доступа успешно обновлена"


class AccessPolicyDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении политики доступа.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Политика доступа успешно удалена"


class AccessRuleResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными правила доступа.

    Attributes:
        message (str): Сообщение о результате операции
        data (AccessRuleSchema): Данные правила доступа
    """

    message: str = "Правило доступа успешно получено"
    data: AccessRuleSchema


class AccessRuleListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком правил доступа.

    Attributes:
        message (str): Сообщение о результате операции
        data (Page[AccessRuleSchema]): Список правил доступа
    """

    message: str = "Список правил доступа успешно получен"
    data: Page[AccessRuleSchema]


class AccessRuleCreateResponseSchema(AccessRuleResponseSchema):
    """
    Схема ответа при создании правила доступа.

    Attributes:
        message (str): Сообщение о результате операции
        data (AccessRuleSchema): Данные созданного правила доступа
    """

    message: str = "Правило доступа успешно создано"


class AccessRuleUpdateResponseSchema(AccessRuleResponseSchema):
    """
    Схема ответа при обновлении правила доступа.

    Attributes:
        message (str): Сообщение о результате операции
        data (AccessRuleSchema): Данные обновленного правила доступа
    """

    message: str = "Правило доступа успешно обновлено"


class AccessRuleDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении правила доступа.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Правило доступа успешно удалено"


class UserPermissionsResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком разрешений пользователя для ресурса.

    Attributes:
        message (str): Сообщение о результате операции
        data (List[str]): Список разрешений пользователя
    """

    message: str = "Список разрешений пользователя успешно получен"
    data: List[str]


class UserAccessSettingsResponseSchema(BaseResponseSchema):
    """
    Схема ответа с настройками доступа пользователя.

    Attributes:
        message (str): Сообщение о результате операции
        data (UserAccessSettingsSchema): Данные настроек доступа пользователя
    """

    message: str = "Настройки доступа пользователя успешно получены"
    data: UserAccessSettingsSchema


class PermissionCheckResponseSchema(BaseResponseSchema):
    """
    Схема ответа
    """

    message: str = "Настройки доступа пользователя успешно получены"
    data: UserAccessSettingsSchema
