from typing import List
from pydantic import Field

from app.schemas.v1.base import  BaseResponseSchema

class PermissionCheckResponseSchema(BaseResponseSchema):
    """Схема для ответа на запрос проверки разрешения"""
    has_permission: bool = Field(..., description="Результат проверки разрешения")
    resource_type: str = Field(..., description="Тип ресурса")
    resource_id: int = Field(..., description="ID ресурса")
    permission: str = Field(..., description="Тип разрешения")


class UserPermissionsResponseSchema(BaseResponseSchema):
    """Схема для ответа на запрос получения разрешений пользователя"""
    resource_type: str = Field(..., description="Тип ресурса")
    resource_id: int = Field(..., description="ID ресурса")
    permissions: List[str] = Field(..., description="Список разрешений")
