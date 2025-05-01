from typing import Any, Dict, Optional, Union

from pydantic import Field

from app.models.v1.access import PermissionType, ResourceType
from app.schemas.v1.base import BaseRequestSchema


class PermissionCheckRequestSchema(BaseRequestSchema):
    """Схема для запроса проверки разрешения"""

    resource_type: Union[ResourceType, str] = Field(..., description="Тип ресурса")
    resource_id: int = Field(..., description="ID ресурса")
    permission: Union[PermissionType, str] = Field(..., description="Тип разрешения")
    context: Optional[Dict[str, Any]] = Field(None, description="Контекст выполнения")


class UpdateUserAccessSettingsSchema(BaseRequestSchema):
    """
    Схема для обновления настроек доступа пользователя.
    """

    default_workspace_id: Optional[int] = Field(
        None, description="ID рабочего пространства по умолчанию"
    )
    default_permission: Optional[Union[PermissionType, str]] = Field(
        None, description="Разрешение по умолчанию для новых ресурсов"
    )
