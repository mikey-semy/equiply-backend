from typing import TYPE_CHECKING

from app.models.v1.base import BaseModel
from app.models.v1.workspaces import WorkspaceRole

__all__ = ["BaseModel", "WorkspaceRole"]

if TYPE_CHECKING:
    from app.models.v1.modules.ai import AISettingsModel
    from app.models.v1.modules.lists import ListDefinitionModel, ListItemModel
    from app.models.v1.modules.tables import (TableDefinitionModel,
                                              TableRowModel)
    from app.models.v1.modules.templates import ModuleTemplateModel
    from app.models.v1.users import UserModel
    from app.models.v1.workspaces import WorkspaceMemberModel, WorkspaceModel
