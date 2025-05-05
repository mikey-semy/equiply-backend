"""
Пакет моделей данных.

Предоставляет единую точку доступа ко всем моделям приложения.
"""
from app.models.v1.groups import (UserGroupModel, UserGroupMemberModel)
from app.models.v1.access import (AccessPolicyModel, AccessRuleModel,
                                  DefaultPolicyModel, PermissionType,
                                  ResourceType, SubjectType,
                                  UserAccessSettingsModel)
from app.models.v1.base import BaseModel
from app.models.v1.integrations import (IntegrationType, LinkedItemModel,
                                        ModuleIntegrationModel)
from app.models.v1.modules.ai import AIChatModel, AISettingsModel, ModelType
from app.models.v1.modules.kanban import (KanbanBoardModel, KanbanCardModel,
                                          KanbanColumnModel)
from app.models.v1.modules.lists import ListDefinitionModel, ListItemModel
from app.models.v1.modules.posts import (ContentType, PostContentBlockModel,
                                         PostModel, PostStatus, PostTagModel,
                                         TagModel)
from app.models.v1.modules.tables import TableDefinitionModel, TableRowModel
from app.models.v1.modules.templates import ModuleTemplateModel
from app.models.v1.users import UserModel, UserRole
from app.models.v1.workspaces import (WorkspaceMemberModel, WorkspaceModel,
                                      WorkspaceRole)

__all__ = [
    "BaseModel",
    "UserModel",
    "UserRole",
    "UserGroupModel",
    "UserGroupMemberModel",
    "WorkspaceModel",
    "ModuleTemplateModel",
    "WorkspaceMemberModel",
    "WorkspaceRole",
    "ModuleIntegrationModel",
    "LinkedItemModel",
    "IntegrationType",
    "KanbanBoardModel",
    "KanbanColumnModel",
    "KanbanCardModel",
    "TableDefinitionModel",
    "TableRowModel",
    "ListDefinitionModel",
    "ListItemModel",
    "AIChatModel",
    "AISettingsModel",
    "ModelType",
    "PostModel",
    "TagModel",
    "PostTagModel",
    "PostContentBlockModel",
    "ContentType",
    "PostStatus",
    "PermissionType",
    "ResourceType",
    "SubjectType",
    "DefaultPolicyModel",
    "AccessPolicyModel",
    "AccessRuleModel",
    "UserAccessSettingsModel",
]
