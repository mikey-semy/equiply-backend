from typing import TYPE_CHECKING
from app.models.v1.base import BaseModel
from app.models.v1.workspaces import WorkspaceRole

__all__ = [
    "BaseModel",
    "WorkspaceRole"
]

if TYPE_CHECKING:
    from app.models.v1.users import UserModel
    from app.models.v1.workspaces import WorkspaceModel, WorkspaceMemberModel
    from app.models.v1.module_tables import TableDefinitionModel, TableRowModel
    from app.models.v1.module_lists import ListDefinitionModel, ListItemModel
    from app.models.v1.module_templates import ModuleTemplateModel