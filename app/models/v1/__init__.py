from typing import TYPE_CHECKING

from app.models.v1.base import BaseModel
from app.models.v1.users import UserRole
from app.models.v1.workspaces import WorkspaceRole

__all__ = ["BaseModel", "WorkspaceRole", "UserRole"]

if TYPE_CHECKING:
    from app.models.v1.groups import (UserGroupModel, UserGroupMemberModel)
    from app.models.v1.access import (AccessPolicyModel, AccessRuleModel,
                                      DefaultPolicyModel,
                                      UserAccessSettingsModel)
    from app.models.v1.integrations import (IntegrationType, LinkedItemModel,
                                            ModuleIntegrationModel)
    from app.models.v1.modules.ai import (AIChatModel, AISettingsModel,
                                          ModelType)
    from app.models.v1.modules.kanban import (KanbanBoardModel,
                                              KanbanCardModel,
                                              KanbanColumnModel)
    from app.models.v1.modules.lists import ListDefinitionModel, ListItemModel
    from app.models.v1.modules.posts import (ContentType,
                                             PostContentBlockModel, PostModel,
                                             PostStatus, PostTagModel,
                                             TagModel)
    from app.models.v1.modules.tables import (TableDefinitionModel,
                                              TableRowModel)
    from app.models.v1.modules.templates import ModuleTemplateModel
    from app.models.v1.users import UserModel
    from app.models.v1.workspaces import WorkspaceMemberModel, WorkspaceModel
