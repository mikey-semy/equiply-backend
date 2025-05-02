from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from app.models.v1.access import PermissionType, ResourceType
from app.schemas.v1.base import BaseRequestSchema


class AccessPolicyCreateRequestSchema(BaseRequestSchema):
    """
    Схема для создания новой политики доступа.

    Используется в запросах на создание политик доступа. Не содержит полей id,
    created_at и updated_at, так как они генерируются на стороне сервера.

    Attributes:
        name (str): Название политики, используемое для идентификации в интерфейсе
        description (Optional[str]): Подробное описание назначения и применения политики
        resource_type (Union[ResourceType, str]): Тип ресурса, к которому применяется политика
        permissions (List[Union[PermissionType, str]]): Список разрешений, предоставляемых политикой
        conditions (Dict[str, Any]): Условия применения политики в формате JSON
        priority (int): Приоритет политики (целое число)
        is_active (bool): Флаг активности политики
        is_public (bool): Флаг публичности политики
        workspace_id (Optional[int]): ID рабочего пространства, к которому относится политика
    """

    name: str = Field(
        ...,
        description="Название политики, используемое для идентификации в интерфейсе",
    )
    description: Optional[str] = Field(
        None, description="Подробное описание назначения и применения политики"
    )
    resource_type: Union[ResourceType, str] = Field(
        ...,
        description="Тип ресурса, к которому применяется политика (например, WORKSPACE, TABLE, LIST)",
    )
    permissions: List[Union[PermissionType, str]] = Field(
        ...,
        description="""
        Список разрешений, предоставляемых политикой.

        Представлен в виде списка для удобства использования API. Возможные значения:
        - READ: разрешение на чтение ресурса
        - WRITE: разрешение на изменение ресурса
        - DELETE: разрешение на удаление ресурса
        - MANAGE: разрешение на управление ресурсом (настройки, права)
        - ADMIN: полный административный доступ
        - CUSTOM: пользовательское разрешение

        Пример: ["read", "write", "manage"]
        """,
    )
    conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Условия применения политики в формате JSON. Могут включать временные ограничения, IP-адреса и другие контекстные параметры",
    )
    priority: int = Field(
        default=0,
        description="Приоритет политики (целое число). При конфликте применяется политика с более высоким приоритетом",
    )
    is_active: bool = Field(
        default=True,
        description="Флаг активности политики. Неактивные политики не применяются при проверке доступа",
    )
    is_public: bool = Field(
        default=False,
        description="Флаг публичности политики. Публичные политики видны всем пользователям системы",
    )
    workspace_id: Optional[int] = Field(
        None,
        description="ID рабочего пространства, к которому относится политика. Если не указан, политика считается глобальной",
    )


class AccessPolicyUpdateRequestSchema(BaseRequestSchema):
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

    name: Optional[str] = Field(None, description="Новое название политики")
    description: Optional[str] = Field(None, description="Новое описание политики")
    conditions: Optional[Dict[str, Any]] = Field(
        None, description="Новые условия применения политики в формате JSON"
    )
    permissions: Optional[List[Union[PermissionType, str]]] = Field(
        None,
        description="""
        Новый список разрешений, предоставляемых политикой.

        Полностью заменяет существующий список разрешений.
        Пример: ["read", "write", "manage"]
        """,
    )
    priority: Optional[int] = Field(None, description="Новый приоритет политики")
    is_active: Optional[bool] = Field(
        None, description="Новый статус активности политики"
    )
    is_public: Optional[bool] = Field(
        None, description="Новый статус публичности политики"
    )


class AccessRuleCreateRequestSchema(BaseRequestSchema):
    """
    Схема для создания нового правила доступа.

    Определяет все необходимые поля для создания правила доступа, связывающего
    политику доступа с конкретным ресурсом и субъектом.

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
        ..., description="ID политики доступа, которая применяется в данном правиле"
    )
    resource_id: int = Field(
        ..., description="ID конкретного ресурса, к которому применяется правило"
    )
    resource_type: Union[ResourceType, str] = Field(
        ...,
        description="Тип ресурса, к которому применяется правило. Должен соответствовать типу в политике",
    )
    subject_id: int = Field(
        ...,
        description="ID субъекта (пользователя или группы), к которому применяется правило",
    )
    subject_type: str = Field(
        ...,
        description="Тип субъекта: 'user' для пользователя или 'group' для группы пользователей",
    )
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Дополнительные атрибуты правила в формате JSON. Могут переопределять или дополнять условия политики",
    )
    is_active: bool = Field(
        default=True,
        description="Флаг активности правила. Неактивные правила не применяются при проверке доступа",
    )
    is_public: bool = Field(
        default=False,
        description="Флаг публичности правила. Если True, правило применяется ко всем пользователям, независимо от политики",
    )


class AccessRuleUpdateRequestSchema(BaseRequestSchema):
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
        None, description="Новые дополнительные атрибуты правила в формате JSON"
    )
    is_active: Optional[bool] = Field(
        None, description="Новый статус активности правила"
    )
    is_public: Optional[bool] = Field(
        None, description="Новый статус публичности правила"
    )


class PermissionCheckRequestSchema(BaseRequestSchema):
    """
    Схема для запроса проверки разрешения.

    Используется для проверки наличия определенного разрешения у пользователя
    для конкретного ресурса.

    Attributes:
        resource_type (Union[ResourceType, str]): Тип ресурса
        resource_id (int): ID ресурса
        permission (Union[PermissionType, str]): Тип разрешения
        context (Optional[Dict[str, Any]]): Контекст выполнения
    """

    resource_type: Union[ResourceType, str] = Field(..., description="Тип ресурса")
    resource_id: int = Field(..., description="ID ресурса")
    permission: Union[PermissionType, str] = Field(..., description="Тип разрешения")
    context: Optional[Dict[str, Any]] = Field(None, description="Контекст выполнения")


class UpdateUserAccessSettingsSchema(BaseRequestSchema):
    """
    Схема для обновления настроек доступа пользователя.

    Позволяет изменить настройки доступа по умолчанию для пользователя.

    Attributes:
        default_workspace_id (Optional[int]): ID рабочего пространства по умолчанию
        default_permission (Optional[Union[PermissionType, str]]): Разрешение по умолчанию для новых ресурсов
    """

    default_workspace_id: Optional[int] = Field(
        None, description="ID рабочего пространства по умолчанию"
    )
    default_permission: Optional[Union[PermissionType, str]] = Field(
        None, description="Разрешение по умолчанию для новых ресурсов"
    )
