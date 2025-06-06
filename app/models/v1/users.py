"""
Модуль, содержащий модели данных для работы с пользователями.

Этот модуль определяет следующие модели SQLAlchemy:
- UserModel: представляет пользователя в системе.

Модель наследуется от базового класса BaseModel и определяет
соответствующие поля и отношения между таблицами базы данных.

Модель использует типизированные аннотации Mapped для определения полей,
что обеспечивает улучшенную поддержку статической типизации.

Этот модуль предназначен для использования в сочетании с SQLAlchemy ORM
для выполнения операций с базой данных, связанных с пользователями.
"""

from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1.base import BaseModel
from app.models.v1.modules.work_permits import ElectricalSafetyGroup

if TYPE_CHECKING:
    from app.models.v1.groups import UserGroupMemberModel
    from app.models.v1.access import AccessPolicyModel, UserAccessSettingsModel
    from app.models.v1.modules.ai import AIChatModel, AISettingsModel
    from app.models.v1.modules.posts import PostModel
    from app.models.v1.modules.templates import ModuleTemplateModel
    from app.models.v1.workspaces import WorkspaceMemberModel, WorkspaceModel
    from app.models.v1.dictionaries import ProfessionModel, SubdivisionModel

class UserRole(str, Enum):
    """
    Роли пользователя в системе.

    Attributes:
        ADMIN (str): Роль администратора.
        MODERATOR (str): Роль модератора.
        USER (str): Роль пользователя.
    """

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class UserModel(BaseModel):
    """
    Модель для представления пользователей.

    Attributes:
        username (str): Имя пользователя.
        email (str): Электронная почта пользователя.
        phone (str): Номер телефона пользователя.
        hashed_password (str): Хэшированный пароль пользователя.
        role (UserRole): Роль пользователя в системе.
        avatar (str): Ссылка на аватар пользователя.
        is_active (bool): Флаг активности пользователя.
        is_verified (bool): Флаг подтверждения email пользователя.
        vk_id (int): ID пользователя в VK.
        google_id (str): ID пользователя в Google.
        yandex_id (int): ID пользователя в Yandex.
        electrical_safety_group (ElectricalSafetyGroup): Группа электробезопасности пользователя.
        profession_id (int): ID профессии пользователя.
        subdivision_id (int): ID подразделения пользователя.

    Relationships:
        profession_ref (ProfessionModel): Ссылка на профессию пользователя.
        subdivision_ref (SubdivisionModel): Ссылка на подразделение пользователя.
        owned_workspaces (List[WorkspaceModel]): Рабочие пространства, принадлежащие пользователю.
        workspaces (List[WorkspaceMemberModel]): Рабочие пространства, в которых пользователь является участником.
        created_templates (List[ModuleTemplateModel]): Шаблоны модулей, созданные пользователем.
        ai_settings (AISettingsModel): Настройки ИИ пользователя.
        posts (List[PostModel]): Публикации, созданные пользователем.
        owned_policies (List[AccessPolicyModel]): Политики доступа, принадлежащие пользователю.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    avatar: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    vk_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    google_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    yandex_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    electrical_safety_group: Mapped[Optional[ElectricalSafetyGroup]] = mapped_column(nullable=True)
    profession_id: Mapped[Optional[int]] = mapped_column(ForeignKey("professions.id"), nullable=True)
    subdivision_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subdivisions.id"), nullable=True)

    profession_ref: Mapped[Optional["ProfessionModel"]] = relationship(
        "ProfessionModel", back_populates="users"
    )

    subdivision_ref: Mapped[Optional["SubdivisionModel"]] = relationship(
        "SubdivisionModel", back_populates="users"
    )

    group_memberships: Mapped[List["UserGroupMemberModel"]] = relationship(
        "UserGroupMemberModel", back_populates="user", cascade="all, delete-orphan"
    )

    owned_workspaces: Mapped[List["WorkspaceModel"]] = relationship(
        "WorkspaceModel", foreign_keys="WorkspaceModel.owner_id", back_populates="owner"
    )

    workspace_memberships: Mapped[List["WorkspaceMemberModel"]] = relationship(
        "WorkspaceMemberModel", back_populates="user", cascade="all, delete-orphan"
    )

    created_templates: Mapped[List["ModuleTemplateModel"]] = relationship(
        "ModuleTemplateModel", back_populates="creator", cascade="all, delete-orphan"
    )

    ai_chats: Mapped[List["AIChatModel"]] = relationship(
        "AIChatModel", back_populates="user", cascade="all, delete-orphan"
    )

    ai_settings: Mapped["AISettingsModel"] = relationship(
        "AISettingsModel", back_populates="user", uselist=False
    )

    posts: Mapped[List["PostModel"]] = relationship(
        "PostModel", back_populates="author", cascade="all, delete-orphan"
    )

    owned_policies: Mapped[List["AccessPolicyModel"]] = relationship(
        "AccessPolicyModel",
        back_populates="owner",
        foreign_keys="AccessPolicyModel.owner_id",
    )

    access_settings: Mapped["UserAccessSettingsModel"] = relationship(
        "UserAccessSettingsModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
