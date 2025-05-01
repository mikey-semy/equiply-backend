from typing import Any, Dict, List, Optional, Union
from pydantic import Field

from app.schemas.v1.base import BaseSchema, CommonBaseSchema
from app.models.v1.access import PermissionType, ResourceType

class DefaultPolicySchema(BaseSchema):
    """
    Схема базовой политики доступа.

    Базовые политики доступа используются как шаблоны для создания
    политик доступа в рабочих пространствах. Они определяют стандартные
    наборы разрешений для различных типов ресурсов и ролей пользователей.

    Attributes:
        name (str): Название политики, используемое для идентификации в интерфейсе
        description (Optional[str]): Подробное описание назначения и применения политики
        resource_type (str): Тип ресурса, к которому применяется политика
        permissions (List[str]): Список разрешений, предоставляемых политикой
        conditions (Optional[Dict[str, Any]]): Условия применения политики в формате JSON
        priority (int): Приоритет политики (целое число)
        is_active (bool): Флаг активности политики
        is_system (bool): Флаг системной политики (не может быть удалена пользователем)
    """
    name: str = Field(
        ...,
        description="Название политики, используемое для идентификации в интерфейсе"
    )
    description: Optional[str] = Field(
        None,
        description="Подробное описание назначения и применения политики"
    )
    resource_type: str = Field(
        ...,
        description="Тип ресурса, к которому применяется политика (например, WORKSPACE, TABLE, LIST)"
    )
    permissions: List[str] = Field(
        ...,
        description="""
        Список разрешений, предоставляемых политикой.

        Возможные значения:
        - READ: разрешение на чтение ресурса
        - WRITE: разрешение на изменение ресурса
        - DELETE: разрешение на удаление ресурса
        - MANAGE: разрешение на управление ресурсом (настройки, права)
        - ADMIN: полный административный доступ

        Пример: ["read", "write", "manage"]
        """
    )
    conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Условия применения политики в формате JSON. Могут включать временные ограничения, IP-адреса и другие контекстные параметры"
    )
    priority: int = Field(
        default=0,
        description="Приоритет политики (целое число). При конфликте применяется политика с более высоким приоритетом"
    )
    is_active: bool = Field(
        default=True,
        description="Флаг активности политики. Неактивные политики не применяются при проверке доступа"
    )
    is_system: bool = Field(
        default=False,
        description="Флаг системной политики. Системные политики не могут быть удалены пользователем и используются как шаблоны"
    )


class AccessPolicyBaseSchema(BaseSchema):
    """
    Базовая схема для политики доступа.

    Политика доступа определяет набор разрешений и условий, которые могут быть
    применены к определенным ресурсам системы.

    Attributes:
        name (str): Название политики, используемое для идентификации в интерфейсе
        description (Optional[str]): Подробное описание назначения и применения политики
        resource_type (Union[ResourceType, str]): Тип ресурса, к которому применяется политика
        conditions (Dict[str, Any]): Условия применения политики в формате JSON
        permissions (List[Union[PermissionType, str]]): Список разрешений, предоставляемых политикой
        priority (int): Приоритет политики (целое число)
        is_active (bool): Флаг активности политики
        is_public (bool): Флаг публичности политики
    """
    name: str = Field(
        ...,
        description="Название политики, используемое для идентификации в интерфейсе"
    )
    description: Optional[str] = Field(
        None,
        description="Подробное описание назначения и применения политики"
    )
    resource_type: Union[ResourceType, str] = Field(
        ...,
        description="Тип ресурса, к которому применяется политика (например, WORKSPACE, TABLE, LIST)"
    )
    conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Условия применения политики в формате JSON. Могут включать временные ограничения, IP-адреса и другие контекстные параметры"
    )
    permissions: List[Union[PermissionType, str]] = Field(
        ...,
        description="""
        Список разрешений, предоставляемых политикой.

        Представлен в виде списка для удобства использования API, хотя в базе данных
        хранится как словарь для большей гибкости. Возможные значения:
        - READ: разрешение на чтение ресурса
        - WRITE: разрешение на изменение ресурса
        - DELETE: разрешение на удаление ресурса
        - MANAGE: разрешение на управление ресурсом (настройки, права)
        - ADMIN: полный административный доступ
        - CUSTOM: пользовательское разрешение

        Пример: ["read", "write", "manage"]
        """
    )
    priority: int = Field(
        default=0,
        description="Приоритет политики (целое число). При конфликте применяется политика с более высоким приоритетом"
    )
    is_active: bool = Field(
        default=True,
        description="Флаг активности политики. Неактивные политики не применяются при проверке доступа"
    )
    is_public: bool = Field(
        default=False,
        description="Флаг публичности политики. Публичные политики видны всем пользователям системы"
    )


class AccessPolicyCreateSchema(AccessPolicyBaseSchema):
    """
    Схема для создания новой политики доступа.

    Расширяет базовую схему политики доступа, добавляя возможность
    указать рабочее пространство, к которому относится политика.

    Attributes:
        workspace_id (Optional[int]): ID рабочего пространства, к которому относится политика
    """
    workspace_id: Optional[int] = Field(
        None,
        description="ID рабочего пространства, к которому относится политика. Если не указан, политика считается глобальной"
    )


class AccessPolicyUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления существующей политики доступа.

    Все поля опциональны, обновляются только предоставленные поля.

    Attributes:
        name (Optional[str]): Новое название политики
        description (Optional[str]): Новое описание политики
        conditions (Optional[Dict[str, Any]]): Новые условия применения политики
        permissions (Optional[List[Union[PermissionType, str]]]): Новый список разрешений
        priority (Optional[int]): Новый приоритет политики
        is_active (Optional[bool]): Новый статус активности политики
        is_public (Optional[bool]): Новый статус публичности политики
    """
    name: Optional[str] = Field(
        None,
        description="Новое название политики"
    )
    description: Optional[str] = Field(
        None,
        description="Новое описание политики"
    )
    conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="Новые условия применения политики в формате JSON"
    )
    permissions: Optional[List[Union[PermissionType, str]]] = Field(
        None,
        description="""
        Новый список разрешений, предоставляемых политикой.

        Полностью заменяет существующий список разрешений.
        Пример: ["read", "write", "manage"]
        """
    )
    priority: Optional[int] = Field(
        None,
        description="Новый приоритет политики"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Новый статус активности политики"
    )
    is_public: Optional[bool] = Field(
        None,
        description="Новый статус публичности политики"
    )


class AccessPolicySchema(AccessPolicyBaseSchema):
    """
    Схема для представления политики доступа в ответах API.

    Расширяет базовую схему, добавляя информацию о владельце и
    рабочем пространстве политики.

    Attributes:
        owner_id (Optional[int]): ID пользователя, создавшего политику
        workspace_id (Optional[int]): ID рабочего пространства, к которому относится политика
    """
    owner_id: Optional[int] = Field(
        None,
        description="ID пользователя, создавшего политику"
    )
    workspace_id: Optional[int] = Field(
        None,
        description="ID рабочего пространства, к которому относится политика. Если None, политика является глобальной"
    )


class AccessRuleBaseSchema(BaseSchema):
    """
    Базовая схема для правила доступа.

    Правило доступа связывает политику доступа с конкретным ресурсом и субъектом
    (пользователем или группой), определяя, как политика применяется в конкретном случае.

    Attributes:
        policy_id (int): ID политики доступа, которая применяется в данном правиле
        resource_id (int): ID конкретного ресурса, к которому применяется правило
        resource_type (Union[ResourceType, str]): Тип ресурса, к которому применяется правило
        subject_id (int): ID субъекта (пользователя или группы), к которому применяется правило
        subject_type (str): Тип субъекта: 'user' для пользователя или 'group' для группы
        attributes (Dict[str, Any]): Дополнительные атрибуты правила в формате JSON
        is_active (bool): Флаг активности правила
        is_public (bool): Флаг публичности правила
    """
    policy_id: int = Field(
        ...,
        description="ID политики доступа, которая применяется в данном правиле"
    )
    resource_id: int = Field(
        ...,
        description="ID конкретного ресурса, к которому применяется правило"
    )
    resource_type: Union[ResourceType, str] = Field(
        ...,
        description="Тип ресурса, к которому применяется правило. Должен соответствовать типу в политике"
    )
    subject_id: int = Field(
        ...,
        description="ID субъекта (пользователя или группы), к которому применяется правило"
    )
    subject_type: str = Field(
        ...,
        description="Тип субъекта: 'user' для пользователя или 'group' для группы пользователей"
    )
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Дополнительные атрибуты правила в формате JSON. Могут переопределять или дополнять условия политики"
    )
    is_active: bool = Field(
        default=True,
        description="Флаг активности правила. Неактивные правила не применяются при проверке доступа"
    )
    is_public: bool = Field(
        default=False,
        description="Флаг публичности правила. Если True, правило применяется ко всем пользователям, независимо от политики"
    )


class AccessRuleCreateSchema(AccessRuleBaseSchema):
    """
    Схема для создания нового правила доступа.

    Идентична базовой схеме правила доступа, так как все поля
    базовой схемы необходимы для создания правила.
    """
    pass


class AccessRuleUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления существующего правила доступа.

    Позволяет обновить атрибуты и статус активности правила.
    Другие параметры правила (политика, ресурс, субъект) не могут быть изменены
    после создания - вместо этого нужно создать новое правило.

    Attributes:
        attributes (Optional[Dict[str, Any]]): Новые дополнительные атрибуты правила
        is_active (Optional[bool]): Новый статус активности правила
        is_public (Optional[bool]): Новый статус публичности правила
    """
    attributes: Optional[Dict[str, Any]] = Field(
        None,
        description="Новые дополнительные атрибуты правила в формате JSON"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Новый статус активности правила"
    )
    is_public: Optional[bool] = Field(
        None,
        description="Новый статус публичности правила"
    )


class AccessRuleSchema(AccessRuleBaseSchema):
    """
    Схема для представления правила доступа в ответах API.

    Расширяет базовую схему, включая полную информацию о связанной
    политике доступа для удобства использования.

    Attributes:
        policy (AccessPolicySchema): Полная информация о политике доступа, связанной с данным правилом
    """
    policy: AccessPolicySchema = Field(
        ...,
        description="Полная информация о политике доступа, связанной с данным правилом"
    )


class UserAccessSettingsSchema(BaseSchema):
    """
    Схема настроек доступа пользователя.

    Содержит персональные настройки пользователя, связанные с доступом к ресурсам.

    Attributes:
        user_id (int): ID пользователя, которому принадлежат настройки
        default_workspace_id (Optional[int]): ID рабочего пространства по умолчанию
        default_permission (Union[PermissionType, str]): Разрешение по умолчанию для новых ресурсов
    """
    user_id: int = Field(
        ...,
        description="ID пользователя, которому принадлежат настройки"
    )
    default_workspace_id: Optional[int] = Field(
        None,
        description="ID рабочего пространства по умолчанию"
    )
    default_permission: Union[PermissionType, str] = Field(
        PermissionType.READ,
        description="Разрешение по умолчанию для новых ресурсов"
    )


class PermissionCheckDataSchema(BaseSchema):
    """
    Схема для ответа на запрос проверки разрешения.

    Содержит результат проверки разрешения пользователя для конкретного ресурса.

    Attributes:
        has_permission (bool): Результат проверки разрешения
        resource_type (str): Тип ресурса
        resource_id (int): ID ресурса
        permission (str): Тип разрешения
    """
    has_permission: bool = Field(
        ...,
        description="Результат проверки разрешения (True - разрешено, False - запрещено)"
    )
    resource_type: str = Field(
        ...,
        description="Тип ресурса, для которого проверялось разрешение"
    )
    resource_id: int = Field(
        ...,
        description="ID ресурса, для которого проверялось разрешение"
    )
    permission: str = Field(
        ...,
        description="Тип разрешения, которое проверялось"
    )


class UserPermissionsDataSchema(BaseSchema):
    """
    Схема для ответа на запрос получения разрешений пользователя.

    Содержит список всех разрешений пользователя для конкретного ресурса.

    Attributes:
        resource_type (str): Тип ресурса
        resource_id (int): ID ресурса
        permissions (List[str]): Список разрешений пользователя
    """
    resource_type: str = Field(
        ...,
        description="Тип ресурса, для которого получены разрешения"
    )
    resource_id: int = Field(
        ...,
        description="ID ресурса, для которого получены разрешения"
    )
    permissions: List[str] = Field(
        ...,
        description="Список разрешений пользователя для данного ресурса"
    )
