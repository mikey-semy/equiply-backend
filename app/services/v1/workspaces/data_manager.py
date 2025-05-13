"""
Менеджер данных для работы с рабочими пространствами.
"""

from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.v1.users import UserModel
from app.models.v1.workspaces import (WorkspaceMemberModel, WorkspaceModel,
                                      WorkspaceRole)
from app.schemas import (PaginationParams, UpdateWorkspaceSchema,
                         WorkspaceDataSchema, WorkspaceMemberDataSchema)
from app.services.v1.base import BaseEntityManager


class WorkspaceDataManager(BaseEntityManager[WorkspaceDataSchema]):
    """
    Менеджер данных для работы с рабочими пространствами.

    Предоставляет методы для выполнения операций с базой данных,
    связанных с рабочими пространствами.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует менеджер данных.

        Args:
            session: Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        super().__init__(
            session=session,
            schema=WorkspaceDataSchema,
            model=WorkspaceModel
        )

    async def create_workspace(
        self, name: str, owner_id: int, description: str = None, is_public: bool = False
    ) -> WorkspaceDataSchema:
        """
        Создает новое рабочее пространство.

        Args:
            name: Название рабочего пространства.
            owner_id: ID владельца.
            description: Описание рабочего пространства.
            is_public: Флаг публичности.

        Returns:
            WorkspaceDataSchema: Созданное рабочее пространство.
        """
        workspace = self.model(
            name=name,
            description=description,
            owner_id=owner_id,
            is_public=is_public
        )
        return await self.add_item(workspace)

    async def get_workspace(self, workspace_id: int) -> Optional[WorkspaceDataSchema]:
        """
        Получает рабочее пространство по ID.

        Args:
            workspace_id: ID рабочего пространства.

        Returns:
            WorkspaceDataSchema: Найденное рабочее пространство или None.
        """
        return await self.get_item(workspace_id)

    async def get_workspace_with_details(
        self, workspace_id: int
    ) -> Optional[WorkspaceModel]:
        """
        Получает рабочее пространство по ID с детальной информацией.

        Args:
            workspace_id: ID рабочего пространства.

        Returns:
            WorkspaceModel: Найденное рабочее пространство с загруженными связями или None.
        """
        statement = (
            select(self.model)
            .options(
                joinedload(self.model.owner),
                selectinload(self.model.members).joinedload(WorkspaceMemberModel.user),
                selectinload(self.model.tables),
                selectinload(self.model.lists),
                selectinload(self.model.kanban_boards),
                selectinload(self.model.posts),
            )
            .where(self.model.id == workspace_id)
        )
        return await self.get_one(statement)

    async def get_user_workspaces(
        self,
        user_id: int,
        pagination: PaginationParams = None,
        search: str = None,
    ) -> Tuple[List[WorkspaceModel], int]:
        """
        Получает список рабочих пространств пользователя.

        Args:
            user_id: ID пользователя.
            pagination: Параметры пагинации.

        Returns:
            Tuple[List[WorkspaceModel], int]: Список рабочих пространств и общее количество.
        """
        # Подзапрос для получения ID рабочих пространств, где пользователь является участником
        member_workspaces = (
            select(WorkspaceMemberModel.workspace_id)
            .where(WorkspaceMemberModel.user_id == user_id)
            .scalar_subquery()
        )

        # Основной запрос для получения рабочих пространств
        statement = select(self.model).distinct()

        # Базовое условие доступа
        access_condition = or_(
            self.model.owner_id == user_id,  # Пользователь - владелец
            self.model.id.in_(member_workspaces),  # Пользователь - участник
            self.model.is_public is True,  # Публичное рабочее пространство
        )

        # Если есть поисковый запрос, добавляем условие поиска
        if search:
            search_condition = or_(
                self.model.name.ilike(f"%{search}%"),
                self.model.description.ilike(f"%{search}%"),
            )
            # Объединяем условия доступа и поиска
            statement = statement.where(and_(access_condition, search_condition))
        else:
            # Если поиска нет, используем только условие доступа
            statement = statement.where(access_condition)

        # Применяем пагинацию, если она указана
        if pagination:
            return await self.get_paginated_items(statement, pagination)

        return await self.get_items(statement)

    async def update_workspace(
        self, workspace_id: int, workspace_data: UpdateWorkspaceSchema
    ) -> Optional[WorkspaceDataSchema]:
        """
        Обновляет рабочее пространство.

        Args:
            workspace_id: ID рабочего пространства.
            workspace_data: Словарь с данными для обновления.

        Returns:
            WorkspaceDataSchema: Обновленное рабочее пространство или None.

        Raises:
            ValueError: Если рабочее пространство не найдено.
        """

        return await self.update_item(workspace_id, workspace_data)

    async def delete_workspace(self, workspace_id: int) -> bool:
        """
        Удаляет рабочее пространство.

        Args:
            workspace_id: ID рабочего пространства.

        Returns:
            bool: True, если рабочее пространство успешно удалено, иначе False.
        """
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            return False

        return await self.delete_item(workspace_id)

    async def get_workspace_member(
        self, workspace_id: int, user_id: int
    ) -> Optional[WorkspaceMemberModel]:
        """
        Получает участника рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя.

        Returns:
            WorkspaceMemberModel: Найденный участник или None.
        """
        statement = select(WorkspaceMemberModel).where(
            and_(
                WorkspaceMemberModel.workspace_id == workspace_id,
                WorkspaceMemberModel.user_id == user_id,
            )
        )
        return await self.get_one(statement)

    async def get_workspace_members(
        self,
        workspace_id: int,
        pagination: PaginationParams = None,
        role: WorkspaceRole = None,
        search: str = None,
    ) -> Tuple[List[WorkspaceMemberDataSchema], int]:
        """
        Получает список участников рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            pagination: Параметры пагинации.
            role (WorkspaceRole): Фильтрация по роли участников
            search (str): Поиск по тексту участников

        Returns:
            Tuple[List[WorkspaceMemberDataSchema], int]: Список участников и общее количество.
        """
        # Создаем базовый запрос
        statement = (
            select(WorkspaceMemberModel)
            .options(joinedload(WorkspaceMemberModel.user))
            .where(WorkspaceMemberModel.workspace_id == workspace_id)
        )

        # Поиск по тексту (имя пользователя или email)
        if search:
            statement = statement.join(UserModel).filter(
                or_(
                    UserModel.username.ilike(f"%{search}%"),
                    UserModel.email.ilike(f"%{search}%"),
                )
            )

        # Фильтр по роли пользователя
        if role:
            statement = statement.filter(WorkspaceMemberModel.role == role)

        # Создаем копию запроса для подсчета общего количества
        count_statement = statement.with_only_columns(func.count()).order_by(None)

        # Применяем сортировку
        if pagination:
            if pagination.sort_desc:
                statement = statement.order_by(WorkspaceMemberModel.updated_at.desc())
            else:
                statement = statement.order_by(WorkspaceMemberModel.updated_at.asc())

            # Применяем пагинацию
            statement = statement.offset(pagination.skip).limit(pagination.limit)

        # Выполняем запросы
        try:
            total = await self.session.scalar(count_statement)
            result = await self.session.execute(statement)
            members = result.scalars().all()
        except Exception as e:
            self.logger.error("❌ Ошибка при получении записей: %s", e)
            return [], 0

        member_schemas = []
        for member in members:
            member_data = WorkspaceMemberDataSchema(
                user_id=member.user_id,
                workspace_id=member.workspace_id,
                role=member.role,
                username=member.user.username,
                email=member.user.email,
            )
        member_schemas.append(member_data)
        return member_schemas, total

    async def add_workspace_member(
        self,
        workspace_id: int,
        user_id: int,
        role: WorkspaceRole = WorkspaceRole.VIEWER,
    ) -> WorkspaceMemberModel:
        """
        Добавляет участника в рабочее пространство.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя.
            role: Роль пользователя в рабочем пространстве.

        Returns:
            WorkspaceMemberModel: Созданный участник.
        """
        member = WorkspaceMemberModel(
            workspace_id=workspace_id, user_id=user_id, role=role
        )
        return await self.add_one(member)

    async def update_workspace_member_role(
        self, workspace_id: int, user_id: int, role: WorkspaceRole
    ) -> Optional[WorkspaceMemberModel]:
        """
        Обновляет роль участника рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя.
            role: Новая роль пользователя.

        Returns:
            WorkspaceMemberModel: Обновленный участник или None.
        """
        found_member = await self.get_workspace_member(workspace_id, user_id)

        if not found_member:
            return None

        updated_user = found_member
        updated_user.role = role

        return await self.update_one(found_member, updated_user)

    async def remove_workspace_member(self, workspace_id: int, user_id: int) -> bool:
        """
        Удаляет участника из рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя.

        Returns:
            bool: True, если участник успешно удален, иначе False.
        """
        member = await self.get_workspace_member(workspace_id, user_id)
        if not member:
            return False

        return await self.delete_item(user_id)

    async def check_user_workspace_role(
        self, workspace_id: int, user_id: int
    ) -> Optional[WorkspaceRole]:
        """
        Проверяет роль пользователя в рабочем пространстве.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя.

        Returns:
            WorkspaceRole: Роль пользователя или None, если пользователь не является участником.
        """
        # Сначала проверяем, является ли пользователь владельцем
        workspace = await self.get_workspace(workspace_id)
        if workspace and workspace.owner_id == user_id:
            return WorkspaceRole.OWNER

        # Если не владелец, проверяем членство
        member = await self.get_workspace_member(workspace_id, user_id)
        return member.role if member else None

    async def can_user_access_workspace(self, workspace_id: int, user_id: int) -> bool:
        """
        Проверяет, имеет ли пользователь доступ к рабочему пространству.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя.

        Returns:
            bool: True, если пользователь имеет доступ, иначе False.
        """
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            return False

        # Если рабочее пространство публичное, доступ разрешен всем
        if workspace.is_public:
            return True

        # Если пользователь - владелец, доступ разрешен
        if workspace.owner_id == user_id:
            return True

        # Проверяем, является ли пользователь участником
        member = await self.get_workspace_member(workspace_id, user_id)
        return member is not None

    async def can_user_manage_workspace(
        self,
        workspace_id: int,
        user_id: int,
        required_role: WorkspaceRole = WorkspaceRole.ADMIN,
    ) -> bool:
        """
        Проверяет, имеет ли пользователь права на управление рабочим пространством.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя.
            required_role: Минимальная требуемая роль.

        Returns:
            bool: True, если пользователь имеет права на управление, иначе False.
        """
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            return False

        # Если пользователь - владелец, у него есть все права
        if workspace.owner_id == user_id:
            return True

        # Проверяем роль пользователя
        member = await self.get_workspace_member(workspace_id, user_id)
        if not member:
            return False

        # Проверяем, достаточно ли высока роль пользователя
        role_hierarchy = {
            WorkspaceRole.OWNER: 5,
            WorkspaceRole.ADMIN: 4,
            WorkspaceRole.MODERATOR: 3,
            WorkspaceRole.EDITOR: 2,
            WorkspaceRole.VIEWER: 1,
        }

        return role_hierarchy[member.role] >= role_hierarchy[required_role]
