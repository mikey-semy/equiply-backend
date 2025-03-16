"""
Сервис для работы с рабочими пространствами.
"""
from typing import List, Dict, Any, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    WorkspaceExistsError,
    WorkspaceNotFoundError,
    WorkspaceMemberNotFoundError,
    WorkspaceAccessDeniedError,
    UserNotFoundError
)
from app.models.v1.workspaces import WorkspaceRole
from app.schemas import (
    PaginationParams,
    CurrentUserSchema,
    CreateWorkspaceSchema,
    WorkspaceDataSchema,
    WorkspaceDetailDataSchema,
    WorkspaceMemberDataSchema,
    WorkspaceCreateResponseSchema
)
from app.services.v1.base import BaseService
from app.services.v1.workspaces.data_manager import WorkspaceDataManager
from app.services.v1.users.data_manager import UserDataManager


class WorkspaceService(BaseService):
    """
    Сервис для управления рабочими пространствами.

    Предоставляет методы для создания, получения, обновления и удаления
    рабочих пространств, а также для управления участниками.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис рабочих пространств.

        Args:
            session: Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        super().__init__(session)
        self.data_manager = WorkspaceDataManager(session)
        self.user_data_manager = UserDataManager(session)

    async def create_workspace(
        self,
        new_workspace: CreateWorkspaceSchema,
        current_user: CurrentUserSchema,
    ) -> WorkspaceCreateResponseSchema:
        """
        Создает новое рабочее пространство.

        Args:
            name: Название рабочего пространства.
            current_user: Текущий пользователь (будет владельцем).
            description: Описание рабочего пространства.
            is_public: Флаг публичности.

        Returns:
            WorkspaceCreateResponseSchema: Данные созданного рабочего пространства.
        """
        existing_workspace = await self.data_manager.get_item_by_field("name", new_workspace.name)

        if existing_workspace:
            self.logger.error(
                "Рабочее пространство с названием '%s' уже существует у пользователя %s",
                new_workspace.name,
                current_user.username
            )
            raise WorkspaceExistsError("name", new_workspace.name)

        workspace_schema = await self.data_manager.create_workspace(
            name=new_workspace.name,
            owner_id=current_user.id,
            description=new_workspace.description,
            is_public=new_workspace.is_public
        )

        return WorkspaceCreateResponseSchema(data=workspace_schema)

    async def get_workspaces(
        self,
        current_user: CurrentUserSchema,
        pagination: PaginationParams,
        search: str = None,
    ) -> Tuple[List[WorkspaceDataSchema], int]:
        """
        Получает список рабочих пространств пользователя.

        Args:
            current_user: Текущий пользователь.
            pagination: Параметры пагинации.
            search: Строка поиска.

        Returns:
            Tuple[List[WorkspaceDataSchema], int]: Список рабочих пространств и общее количество.
        """
        return await self.data_manager.get_user_workspaces(
            current_user.id,
            pagination,
            search=search,
        )

    async def get_workspace(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema
    ) -> WorkspaceDataSchema:
        """
        Получает рабочее пространство по ID.

        Args:
            workspace_id: ID рабочего пространства.
            current_user: Текущий пользователь.

        Returns:
            WorkspaceDataSchema: Данные рабочего пространства.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству.
        """
        workspace = await self.data_manager.get_workspace(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        # Проверка доступа
        has_access = await self.data_manager.can_user_access_workspace(
            workspace_id,
            current_user.id
        )
        if not has_access:
            raise WorkspaceAccessDeniedError(workspace_id)

        return WorkspaceDataSchema.from_orm(workspace)

    async def get_workspace_details(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema
    ) -> WorkspaceDetailDataSchema:
        """
        Получает детальную информацию о рабочем пространстве.

        Args:
            workspace_id: ID рабочего пространства.
            current_user: Текущий пользователь.

        Returns:
            WorkspaceDetailDataSchema: Детальные данные рабочего пространства.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству.
        """
        workspace = await self.data_manager.get_workspace_with_details(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        # Проверка доступа
        has_access = await self.data_manager.can_user_access_workspace(
            workspace_id,
            current_user.id
        )
        if not has_access:
            raise WorkspaceAccessDeniedError(workspace_id)

        # Формируем детальные данные
        workspace_data = WorkspaceDetailDataSchema.from_orm(workspace)
        workspace_data.tables_count = len(workspace.tables)
        workspace_data.lists_count = len(workspace.lists)

        # Преобразуем данные участников
        members_data = []
        for member in workspace.members:
            member_data = WorkspaceMemberDataSchema(
                user_id=member.user_id,
                workspace_id=member.workspace_id,
                role=member.role,
                username=member.user.username,
                email=member.user.email
            )
            members_data.append(member_data)

        workspace_data.members = members_data

        return workspace_data



    async def update_workspace(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema,
        data: Dict[str, Any]
    ) -> WorkspaceDataSchema:
        """
        Обновляет рабочее пространство.

        Args:
            workspace_id: ID рабочего пространства.
            current_user: Текущий пользователь.
            data: Данные для обновления.

        Returns:
            WorkspaceDataSchema: Данные обновленного рабочего пространства.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceAccessDeniedError: Если у пользователя нет прав на обновление.
        """
        workspace = await self.data_manager.get_workspace(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        # Проверка прав доступа (только владелец или администратор могут обновлять)
        can_manage = await self.data_manager.can_user_manage_workspace(
            workspace_id,
            current_user.id,
            WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.ADMIN.value,
                "У вас нет прав на обновление рабочего пространства"
            )

        updated_workspace = await self.data_manager.update_workspace(workspace_id, data)
        return WorkspaceDataSchema.from_orm(updated_workspace)

    async def delete_workspace(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema
    ) -> bool:
        """
        Удаляет рабочее пространство.

        Args:
            workspace_id: ID рабочего пространства.
            current_user: Текущий пользователь.

        Returns:
            bool: True, если рабочее пространство успешно удалено.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceAccessDeniedError: Если у пользователя нет прав на удаление.
        """
        workspace = await self.data_manager.get_workspace(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        # Только владелец может удалить рабочее пространство
        if workspace.owner_id != current_user.id:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.OWNER.value,
                "Только владелец может удалить рабочее пространство"
            )

        success = await self.data_manager.delete_workspace(workspace_id)
        return success

    async def get_workspace_members(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema,
        pagination: PaginationParams = None
    ) -> Tuple[List[WorkspaceMemberDataSchema], int]:
        """
        Получает список участников рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            current_user: Текущий пользователь.
            pagination: Параметры пагинации.

        Returns:
            Tuple[List[WorkspaceMemberDataSchema], int]: Список участников и общее количество.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству.
        """
        # Проверка существования рабочего пространства
        workspace = await self.data_manager.get_workspace(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        # Проверка доступа
        has_access = await self.data_manager.can_user_access_workspace(
            workspace_id,
            current_user.id
        )
        if not has_access:
            raise WorkspaceAccessDeniedError(workspace_id)

        # Получение участников
        members, total = await self.data_manager.get_workspace_members(workspace_id, pagination)

        # Преобразование в схему данных
        members_data = []
        for member in members:
            member_data = WorkspaceMemberDataSchema(
                user_id=member.user_id,
                workspace_id=member.workspace_id,
                role=member.role,
                username=member.user.username,
                email=member.user.email
            )
            members_data.append(member_data)

        return members_data, total

    async def add_workspace_member(
        self,
        workspace_id: int,
        user_id: int,
        role: WorkspaceRole,
        current_user: CurrentUserSchema
    ) -> WorkspaceMemberDataSchema:
        """
        Добавляет участника в рабочее пространство.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя для добавления.
            role: Роль пользователя в рабочем пространстве.
            current_user: Текущий пользователь.

        Returns:
            WorkspaceMemberDataSchema: Данные добавленного участника.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            UserNotFoundError: Если пользователь не найден.
            WorkspaceAccessDeniedError: Если у текущего пользователя нет прав на добавление участников.
        """
        # Проверка существования рабочего пространства
        workspace = await self.data_manager.get_workspace(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        # Проверка существования пользователя
        user = await self.user_data_manager.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Проверка прав доступа (только владелец или администратор могут добавлять участников)
        can_manage = await self.data_manager.can_user_manage_workspace(
            workspace_id,
            current_user.id,
            WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.ADMIN.value,
                "У вас нет прав на добавление участников"
            )

        # Проверка, не является ли пользователь уже участником
        existing_member = await self.data_manager.get_workspace_member(workspace_id, user_id)
        if existing_member:
            # Если пользователь уже участник, обновляем его роль
            member = await self.data_manager.update_workspace_member_role(workspace_id, user_id, role)
        else:
            # Иначе добавляем нового участника
            member = await self.data_manager.add_workspace_member(workspace_id, user_id, role)

        # Формируем ответ
        return WorkspaceMemberDataSchema(
            user_id=user_id,
            workspace_id=workspace_id,
            role=role,
            username=user.username,
            email=user.email
        )

    async def update_workspace_member_role(
        self,
        workspace_id: int,
        user_id: int,
        role: WorkspaceRole,
        current_user: CurrentUserSchema
    ) -> WorkspaceMemberDataSchema:
        """
        Обновляет роль участника рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя.
            role: Новая роль пользователя.
            current_user: Текущий пользователь.

        Returns:
            WorkspaceMemberDataSchema: Данные участника с обновленной ролью.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceMemberNotFoundError: Если участник не найден.
            WorkspaceAccessDeniedError: Если у текущего пользователя нет прав на обновление ролей.
        """
        # Проверка существования рабочего пространства
        workspace = await self.data_manager.get_workspace(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        # Проверка существования участника
        member = await self.data_manager.get_workspace_member(workspace_id, user_id)
        if not member:
            raise WorkspaceMemberNotFoundError(workspace_id, user_id)

        # Проверка прав доступа (только владелец или администратор могут обновлять роли)
        can_manage = await self.data_manager.can_user_manage_workspace(
            workspace_id,
            current_user.id,
            WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.ADMIN.value,
                "У вас нет прав на обновление ролей участников"
            )

        # Запрет на изменение роли владельца
        if workspace.owner_id == user_id:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                detail="Невозможно изменить роль владельца рабочего пространства"
            )

        # Обновление роли
        updated_member = await self.data_manager.update_workspace_member_role(
            workspace_id,
            user_id,
            role
        )

        # Получение данных пользователя для ответа
        user = await self.user_data_manager.get_user_by_id(user_id)

        # Формируем ответ
        return WorkspaceMemberDataSchema(
            user_id=user_id,
            workspace_id=workspace_id,
            role=role,
            username=user.username,
            email=user.email
        )

    async def remove_workspace_member(
        self,
        workspace_id: int,
        user_id: int,
        current_user: CurrentUserSchema
    ) -> bool:
        """
        Удаляет участника из рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя для удаления.
            current_user: Текущий пользователь.

        Returns:
            bool: True, если участник успешно удален.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceMemberNotFoundError: Если участник не найден.
            WorkspaceAccessDeniedError: Если у текущего пользователя нет прав на удаление участников.
        """
        # Проверка существования рабочего пространства
        workspace = await self.data_manager.get_workspace(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        # Проверка существования участника
        member = await self.data_manager.get_workspace_member(workspace_id, user_id)
        if not member:
            raise WorkspaceMemberNotFoundError(workspace_id, user_id)

        # Запрет на удаление владельца
        if workspace.owner_id == user_id:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                detail="Невозможно удалить владельца рабочего пространства"
            )

        # Пользователь может удалить сам себя из рабочего пространства
        if current_user.id == user_id:
            return await self.data_manager.remove_workspace_member(workspace_id, user_id)

        # Проверка прав доступа (только владелец или администратор могут удалять участников)
        can_manage = await self.data_manager.can_user_manage_workspace(
            workspace_id,
            current_user.id,
            WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.ADMIN.value,
                "У вас нет прав на удаление участников"
            )

        # Удаление участника
        return await self.data_manager.remove_workspace_member(workspace_id, user_id)
