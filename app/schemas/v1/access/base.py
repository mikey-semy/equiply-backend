from typing import Any, Dict, List, Optional, Union
from pydantic import Field

from app.schemas.v1.base import BaseSchema, CommonBaseSchema
from app.models.v1.access import PermissionType, ResourceType

class AccessPolicyBaseSchema(BaseSchema):
    """
    Базовая схема для политики доступа.

    Политика доступа определяет набор разрешений и условий, которые могут быть
    применены к определенным ресурсам системы.
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
    """
    workspace_id: Optional[int] = Field(
        None,
        description="ID рабочего пространства, к которому относится политика. Если не указан, политика считается глобальной"
    )

class AccessPolicyUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления существующей политики доступа.

    Все поля опциональны, обновляются только предоставленные поля.
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


class AccessPolicySchema(AccessPolicyBaseSchema):
    """
    Схема для представления политики доступа в ответах API.

    Расширяет базовую схему, добавляя информацию о владельце и
    рабочем пространстве политики.
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

    Правило доступа связывает политику доступа с конкретным ресурсом и субъектом (пользователем или группой),
    определяя, как политика применяется в конкретном случае.
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
    """
    attributes: Optional[Dict[str, Any]] = Field(
        None,
        description="Новые дополнительные атрибуты правила в формате JSON"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Новый статус активности правила"
    )


class AccessRuleSchema(AccessRuleBaseSchema):
    """
    Схема для представления правила доступа в ответах API.

    Расширяет базовую схему, включая полную информацию о связанной
    политике доступа для удобства использования.
    """
    policy: AccessPolicySchema = Field(
        ...,
        description="Полная информация о политике доступа, связанной с данным правилом"
    )