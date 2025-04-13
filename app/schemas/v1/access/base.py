from typing import Any, Dict, List, Optional, Union
from pydantic import Field

from app.schemas.v1.base import BaseSchema, CommonBaseSchema
from app.models.v1.access import PermissionType, ResourceType

class AccessPolicyBaseSchema(BaseSchema):
    """Базовая схема для политики доступа"""
    name: str = Field(..., description="Название политики")
    description: Optional[str] = Field(None, description="Описание политики")
    resource_type: Union[ResourceType, str] = Field(..., description="Тип ресурса")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Условия применения политики")
    permissions: List[Union[PermissionType, str]] = Field(..., description="Разрешения, предоставляемые политикой")
    priority: int = Field(default=0, description="Приоритет политики")
    is_active: bool = Field(default=True, description="Флаг активности политики")


class AccessPolicyCreateSchema(AccessPolicyBaseSchema):
    """Схема для создания политики доступа"""
    workspace_id: Optional[int] = Field(None, description="ID рабочего пространства")


class AccessPolicyUpdateSchema(CommonBaseSchema):
    """Схема для обновления политики доступа"""
    name: Optional[str] = Field(None, description="Название политики")
    description: Optional[str] = Field(None, description="Описание политики")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Условия применения политики")
    permissions: Optional[List[Union[PermissionType, str]]] = Field(None, description="Разрешения, предоставляемые политикой")
    priority: Optional[int] = Field(None, description="Приоритет политики")
    is_active: Optional[bool] = Field(None, description="Флаг активности политики")


class AccessPolicySchema(AccessPolicyBaseSchema):
    """Схема для представления политики доступа"""
    owner_id: Optional[int] = Field(None, description="ID владельца политики")
    workspace_id: Optional[int] = Field(None, description="ID рабочего пространства")


class AccessRuleBaseSchema(BaseSchema):
    """Базовая схема для правила доступа"""
    policy_id: int = Field(..., description="ID политики")
    resource_id: int = Field(..., description="ID ресурса")
    resource_type: Union[ResourceType, str] = Field(..., description="Тип ресурса")
    subject_id: int = Field(..., description="ID субъекта (пользователя или группы)")
    subject_type: str = Field(..., description="Тип субъекта ('user' или 'group')")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные атрибуты правила")
    is_active: bool = Field(default=True, description="Флаг активности правила")


class AccessRuleCreateSchema(AccessRuleBaseSchema):
    """Схема для создания правила доступа"""
    pass


class AccessRuleUpdateSchema(CommonBaseSchema):
    """Схема для обновления правила доступа"""
    attributes: Optional[Dict[str, Any]] = Field(None, description="Дополнительные атрибуты правила")
    is_active: Optional[bool] = Field(None, description="Флаг активности правила")


class AccessRuleSchema(AccessRuleBaseSchema):
    """Схема для представления правила доступа"""
    policy: AccessPolicySchema = Field(..., description="Политика доступа")
