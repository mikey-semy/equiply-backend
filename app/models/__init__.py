"""
Пакет моделей данных.

Предоставляет единую точку доступа ко всем моделям приложения.
"""
from app.models.v1.base import BaseModel

from app.models.v1.users import UserModel
from app.models.v1.workspaces import WorkspaceModel, WorkspaceMemberModel, WorkspaceRole
from app.models.v1.modules.templates import ModuleTemplateModel
from app.models.v1.modules.tables import TableDefinitionModel, TableRowModel
from app.models.v1.modules.lists import ListDefinitionModel, ListItemModel
from app.models.v1.modules.ai import AISettingsModel, ModelType


__all__ = [
    "BaseModel",
    "UserModel",
    "WorkspaceModel",
    "ModuleTemplateModel",
    "WorkspaceMemberModel",
    "WorkspaceRole",
    "TableDefinitionModel",
    "TableRowModel",
    "ListDefinitionModel",
    "ListItemModel",
    "AISettingsModel",
    "ModelType"
]
