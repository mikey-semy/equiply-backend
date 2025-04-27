from typing import Any, Dict, Optional, Union
from pydantic import Field

from app.schemas.v1.base import BaseRequestSchema
from app.models.v1.access import PermissionType, ResourceType


class PermissionCheckRequestSchema(BaseRequestSchema):
    """Схема для запроса проверки разрешения"""
    resource_type: Union[ResourceType, str] = Field(..., description="Тип ресурса")
    resource_id: int = Field(..., description="ID ресурса")
    permission: Union[PermissionType, str] = Field(..., description="Тип разрешения")
    context: Optional[Dict[str, Any]] = Field(None, description="Контекст выполнения")
