from enum import Enum
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.users import UserModel
    from app.models.v1.workspaces import WorkspaceModel

class PermissionType(str, Enum):
    """
    Типы разрешений в системе.
    Attributes:
        READ (str): Разрешение на чтение.
        WRITE (str): Разрешение на запись.
        DELETE (str): Разрешение на удаление.
        MANAGE (str): Разрешение на управление.
        ADMIN (str): Административное разрешение.
        CUSTOM (str): Пользовательское разрешение.
    """
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE = "manage"
    ADMIN = "admin"
    CUSTOM = "custom"

class ResourceType(str, Enum):
    """
    Типы ресурсов в системе.
    Attributes:
        WORKSPACE (str): Рабочее пространство.
        TABLE (str): Таблица.
        LIST (str): Список.
        KANBAN (str): Канбан-доска.
        POST (str): Публикация.
        USER (str): Пользователь.
        CUSTOM (str): Пользовательский тип ресурса.
    """
    WORKSPACE = "workspace"
    TABLE = "table"
    LIST = "list"
    KANBAN = "kanban"
    POST = "post"
    USER = "user"
    CUSTOM = "custom"

class SubjectType(str, Enum):
    """
    Типы субъектов, к которым применяются правила доступа.
    Attributes:
        USER (str): Пользователь.
        GROUP (str): Группа пользователей.
    """
    USER = "user"
    GROUP = "group"

class DefaultPolicyModel(BaseModel):
    """
    Модель для хранения базовых политик доступа.

    Attributes:
        name (str): Название политики.
        description (str): Описание политики.
        resource_type (str): Тип ресурса, к которому применяется политика.
        permissions (Dict[str, Any]): Разрешения, предоставляемые политикой.
        conditions (Dict[str, Any]): Условия доступа в формате JSON.
        priority (int): Приоритет политики.
        is_active (bool): Флаг активности политики.
        is_system (bool): Флаг системной политики (не может быть удалена).
    """
    __tablename__ = "default_policies"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    resource_type: Mapped[str] = mapped_column(nullable=False)
    permissions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default={})
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default={})
    priority: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_system: Mapped[bool] = mapped_column(default=False)

class AccessPolicyModel(BaseModel):
    """
    Модель политики доступа.
    Политика доступа определяет набор правил и условий,
    которые применяются к определенным ресурсам системы.
    Attributes:
        name (str): Название политики.
        description (str): Описание политики.
        resource_type (str): Тип ресурса, к которому применяется политика.
        conditions (Dict[str, Any]): Условия доступа в формате JSON.
        permissions (Dict[str, Any]): Разрешения, предоставляемые политикой.
        priority (int): Приоритет политики (для разрешения конфликтов).
        is_active (bool): Флаг активности политики.
        is_public (bool): Флаг публичности политики.
        owner_id (int): ID владельца политики.
        workspace_id (int): ID рабочего пространства, к которому применяется политика.
    Relationships:
        owner (UserModel): Владелец политики.
        workspace (WorkspaceModel): Рабочее пространство, к которому применяется политика.
        access_rules (List[AccessRuleModel]): Правила доступа, основанные на этой политике.
    """
    __tablename__ = "access_policies"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    resource_type: Mapped[str] = mapped_column(nullable=False)
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default={})
    permissions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default={})
    priority: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_public: Mapped[bool] = mapped_column(default=False)
    owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
    workspace_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workspaces.id"),
        nullable=True
    )

    # Отношения
    owner: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="owned_policies",
        foreign_keys=[owner_id]
    )
    workspace: Mapped["WorkspaceModel"] = relationship(
        "WorkspaceModel",
        back_populates="access_policies"
    )
    access_rules: Mapped[List["AccessRuleModel"]] = relationship(
        "AccessRuleModel",
        back_populates="policy",
        cascade="all, delete-orphan"
    )

class AccessRuleModel(BaseModel):
    """
    Модель правила доступа.
    Правило доступа представляет собой конкретное применение политики доступа
    к определенному ресурсу для определенного субъекта (пользователя или группы).
    Attributes:
        policy_id (int): ID политики доступа.
        resource_id (int): ID ресурса, к которому применяется правило.
        resource_type (str): Тип ресурса.
        subject_id (int): ID субъекта (пользователя или группы).
        subject_type (str): Тип субъекта ("user" или "group").
        attributes (Dict[str, Any]): Дополнительные атрибуты для правила.
        is_active (bool): Флаг активности правила.
    Relationships:
        policy (AccessPolicyModel): Политика доступа, на которой основано правило.
    """
    __tablename__ = "access_rules"

    policy_id: Mapped[int] = mapped_column(
        ForeignKey("access_policies.id"),
        nullable=False
    )
    resource_id: Mapped[int] = mapped_column(nullable=False)
    resource_type: Mapped[str] = mapped_column(nullable=False)
    subject_id: Mapped[int] = mapped_column(nullable=False)
    subject_type: Mapped[str] = mapped_column(nullable=False)
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Отношения
    policy: Mapped["AccessPolicyModel"] = relationship(
        "AccessPolicyModel",
        back_populates="access_rules"
    )

class UserAccessSettingsModel(BaseModel):
    """
    Модель настроек доступа пользователя.

    Хранит персональные настройки пользователя, связанные с доступом к ресурсам.

    Attributes:
        user_id (int): ID пользователя, которому принадлежат настройки.
        default_workspace_id (int): ID рабочего пространства по умолчанию.
        default_permission (str): Разрешение по умолчанию для новых ресурсов.
    """
    __tablename__ = "user_access_settings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )
    default_workspace_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workspaces.id"),
        nullable=True
    )
    default_permission: Mapped[str] = mapped_column(
        nullable=False,
        default="read"
    )

    # Отношения
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="access_settings"
    )
    default_workspace: Mapped[Optional["WorkspaceModel"]] = relationship(
        "WorkspaceModel",
        back_populates="default_for_users"
    )