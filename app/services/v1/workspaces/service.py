"""
Сервис для работы с рабочими пространствами.
"""

from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (UserNotFoundError, WorkspaceAccessDeniedError,
                                 WorkspaceCreationError, WorkspaceExistsError,
                                 WorkspaceMemberNotFoundError,
                                 WorkspaceNotFoundError)
from app.models.v1.workspaces import WorkspaceRole
from app.schemas import (CreateWorkspaceSchema, CurrentUserSchema,
                         PaginationParams, UpdateWorkspaceSchema,
                         WorkspaceCreateResponseSchema, WorkspaceDataSchema,
                         WorkspaceDeleteResponseSchema,
                         WorkspaceDetailDataSchema,
                         WorkspaceMemberAddResponseSchema,
                         WorkspaceMemberDataSchema,
                         WorkspaceMemberRemoveResponseSchema)
from app.services.v1.base import BaseService
from app.services.v1.users.data_manager import UserDataManager
from app.services.v1.workspaces.data_manager import WorkspaceDataManager


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
            new_workspace: Схема создания нового рабочего пространства.
            current_user: Текущий пользователь (будет владельцем).

        Returns:
            WorkspaceCreateResponseSchema: Данные созданного рабочего пространства.

        Raises:
            WorkspaceExistsError: Если рабочее пространство с таким названием уже существует.
            WorkspaceCreationError: Если не удалось создать рабочее пространство.

        Example:
            workspace = await workspace_service.create_workspace(
                new_workspace=CreateWorkspaceSchema(
                    name="My Project",
                    description="Team collaboration workspace",
                    is_public=True
                ),
                current_user=current_user
            )
        """
        existing_workspace = await self.data_manager.filter_by(
            name=new_workspace.name, owner_id=current_user.id
        )

        if existing_workspace:
            self.logger.error(
                "Рабочее пространство с названием '%s' уже существует!",
                new_workspace.name,
            )
            raise WorkspaceExistsError("name", new_workspace.name)

        try:

            workspace_schema = await self.data_manager.create_workspace(
                name=new_workspace.name,
                owner_id=current_user.id,
                description=new_workspace.description,
                is_public=new_workspace.is_public,
            )

            await self.data_manager.add_workspace_member(
                workspace_id=workspace_schema.id,
                user_id=current_user.id,
                role=WorkspaceRole.ADMIN,
            )

            self.logger.info(
                "Создано рабочее пространство '%s' (ID: %s) пользователем %s (ID: %s)",
                new_workspace.name, workspace_schema.id, current_user.username, current_user.id
            )

            return WorkspaceCreateResponseSchema(data=workspace_schema)
        except Exception as e:
            self.logger.error("Ошибка при создании рабочего пространства: %s", str(e))
            raise WorkspaceCreationError() from e

    async def get_workspaces(
        self,
        current_user: CurrentUserSchema,
        pagination: PaginationParams,
        search: str = None,
    ) -> Tuple[List[WorkspaceDataSchema], int]:
        """
        Получает список рабочих пространств для текущего пользователя.

        Args:
            current_user: Текущий пользователь, для которого загружаются рабочие пространства.
            pagination: Параметры пагинации для постраничной загрузки результатов.
            search: Необязательная строка поиска для фильтрации рабочих пространств.

        Returns:
            Кортеж, содержащий список рабочих пространств и общее количество доступных пространств.

        Example:
            Используется для получения списка рабочих пространств с возможностью поиска и разбивки на страницы.
        """
        self.logger.info(
            "Пользователь %s (ID: %s) запросил список рабочих пространств. Параметры: пагинация=%s, поиск='%s'",
            current_user.username, current_user.id, pagination, search
        )

        return await self.data_manager.get_user_workspaces(
            user_id=current_user.id,
            pagination=pagination,
            search=search,
        )

    async def get_workspace(
        self, workspace_id: int, current_user: CurrentUserSchema
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
            workspace_id, current_user.id
        )
        if not has_access:
            raise WorkspaceAccessDeniedError(workspace_id)

        self.logger.info(
            "Пользователь %s (ID: %s) получил информацию о рабочем пространстве %s",
            current_user.username, current_user.id, workspace_id
        )

        return WorkspaceDataSchema.model_validate(workspace)

    async def get_workspace_details(
        self, workspace_id: int, current_user: CurrentUserSchema
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
            workspace_id, current_user.id
        )
        if not has_access:
            raise WorkspaceAccessDeniedError(workspace_id)

        # Получаем участников рабочего пространства
        members = await self.data_manager.get_workspace_members(workspace_id)

        members_data = []

        if members:
            for member in workspace.members:
                member_data = WorkspaceMemberDataSchema(
                    user_id=member.user_id,
                    workspace_id=member.workspace_id,
                    role=member.role,
                    username=member.user.username,
                    email=member.user.email,
                )
                members_data.append(member_data)

        workspace_data = WorkspaceDetailDataSchema(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            owner_id=workspace.owner_id,
            is_public=workspace.is_public,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
            members=members_data,
            tables_count=len(workspace.tables),
            lists_count=len(workspace.lists),
            kanban_boards_count=len(workspace.kanban_boards),
            posts_count=len(workspace.posts),
        )

        self.logger.info(
            "Пользователь %s (ID: %s) получил детальную информацию о рабочем пространстве %s",
            current_user.username, current_user.id, workspace_id
        )

        return workspace_data

    async def update_workspace(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema,
        workspace_data: UpdateWorkspaceSchema,
    ) -> WorkspaceDataSchema:
        """
        Обновляет рабочее пространство.

        Args:
            workspace_id: ID рабочего пространства.
            current_user: Текущий пользователь.
            workspace_data: Данные для обновления рабочего пространства.

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
            workspace_id, current_user.id, WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.ADMIN.value,
                "У вас нет прав на обновление рабочего пространства",
            )

        self.logger.info(
            "Пользователь %s (ID: %s) обновил рабочее пространство %s",
            current_user.username, current_user.id, workspace_id
        )

        try:
            return await self.data_manager.update_workspace(
                workspace_id, workspace_data
            )
        except ValueError as exc:
            raise WorkspaceNotFoundError(workspace_id) from exc

    async def delete_workspace(
        self, workspace_id: int, current_user: CurrentUserSchema
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
                "Только владелец может удалить рабочее пространство",
            )

        # Удаляем рабочее пространство
        await self.data_manager.delete_workspace(workspace_id)

        # Логирование действия
        self.logger.info(
            "Рабочее пространство %s (ID: %s) удалено пользователем %s (ID: %s)",
            workspace.name, workspace_id, current_user.username, current_user.id
        )

        return WorkspaceDeleteResponseSchema()

    async def get_workspace_members(
        self,
        workspace_id: int,
        pagination: PaginationParams,
        role: WorkspaceRole = None,
        search: str = None,
        current_user: CurrentUserSchema = None,
    ) -> Tuple[List[WorkspaceMemberDataSchema], int]:
        """
        Получает список участников рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            pagination: Параметры пагинации.
            role (WorkspaceRole): Фильтрация по роли участников
            search (str): Поиск по тексту участников
            current_user: Текущий пользователь.

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
            workspace_id, current_user.id
        )
        if not has_access:
            raise WorkspaceAccessDeniedError(workspace_id)

        self.logger.info(
            "Пользователь %s (ID: %s) запросил список участников рабочего пространства %s. \
            Параметры: пагинация=%s, роль=%s, поиск='%s'",
            current_user.username, current_user.id, workspace_id, pagination, role, search
        )

        # Получение участников с использованием базового метода
        return await self.data_manager.get_workspace_members(
            workspace_id=workspace_id,
            pagination=pagination,
            role=role,
            search=search,
        )

    async def add_workspace_member(
        self,
        workspace_id: int,
        user_id: int,
        role: WorkspaceRole,
        current_user: CurrentUserSchema,
    ) -> WorkspaceMemberAddResponseSchema:
        """
        Добавляет участника в рабочее пространство.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя для добавления.
            role: Роль пользователя в рабочем пространстве.
            current_user: Текущий пользователь.

        Returns:
            WorkspaceMemberAddResponseSchema: Сообщение об удачном добавлении пользователя в рабочее пространство

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
        user = await self.user_data_manager.get_item(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Проверка прав доступа (только владелец или администратор могут добавлять участников)
        can_manage = await self.data_manager.can_user_manage_workspace(
            workspace_id, current_user.id, WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.ADMIN.value,
                "У вас нет прав на добавление участников",
            )

        # Проверка, не является ли пользователь уже участником
        existing_member = await self.data_manager.get_workspace_member(
            workspace_id, user_id
        )
        if existing_member:
            # Если пользователь уже участник, обновляем его роль
            await self.data_manager.update_workspace_member_role(
                workspace_id, user_id, role
            )
        else:
            # Иначе добавляем нового участника
            await self.data_manager.add_workspace_member(workspace_id, user_id, role)

        # Формируем данные участника
        member_data = WorkspaceMemberDataSchema(
            user_id=user_id,
            workspace_id=workspace_id,
            role=role,
            username=user.username,
            email=user.email,
        )

        self.logger.info(
            "Пользователь %s (ID: %s) добавил участника (ID: %s) с ролью %s в рабочее пространство %s",
            current_user.username, current_user.id, user_id, role.value, workspace_id
        )

        # Возвращаем полный ответ с данными
        return WorkspaceMemberAddResponseSchema(data=member_data)

    async def update_workspace_member_role(
        self,
        workspace_id: int,
        user_id: int,
        role: WorkspaceRole,
        current_user: CurrentUserSchema,
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
            workspace_id, current_user.id, WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.ADMIN.value,
                "У вас нет прав на обновление ролей участников",
            )

        # Запрет на изменение роли владельца
        if workspace.owner_id == user_id:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                detail="Невозможно изменить роль владельца рабочего пространства",
            )

        # Обновление роли
        updated_member = await self.data_manager.update_workspace_member_role(
            workspace_id, user_id, role
        )

        # Дополнительная проверка на случай, если что-то пошло не так
        if not updated_member:
            raise UserNotFoundError(field="id", value=user_id)

        # Получение данных пользователя для ответа
        user = await self.user_data_manager.get_item(user_id)

        self.logger.info(
            "Пользователь %s (ID: %s) обновил роль участника (ID: %s) на %s в рабочем пространстве %s",
            current_user.username, current_user.id, user_id, role.value, workspace_id
        )

        # Формируем ответ
        return WorkspaceMemberDataSchema(
            user_id=user_id,
            workspace_id=workspace_id,
            role=role,
            username=user.username,
            email=user.email,
        )

    async def remove_workspace_member(
        self, workspace_id: int, user_id: int, current_user: CurrentUserSchema
    ) -> WorkspaceMemberRemoveResponseSchema:
        """
        Удаляет участника из рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            user_id: ID пользователя для удаления.
            current_user: Текущий пользователь.

        Returns:
            WorkspaceMemberRemoveResponseSchema: сообщение об удалении участника рабочего пространства.

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
                detail="Невозможно удалить владельца рабочего пространства",
            )

        # Пользователь может удалить сам себя из рабочего пространства
        if current_user.id == user_id:
            return await self.data_manager.remove_workspace_member(
                workspace_id, user_id
            )

        # Проверка прав доступа (только владелец или администратор могут удалять участников)
        can_manage = await self.data_manager.can_user_manage_workspace(
            workspace_id, current_user.id, WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                WorkspaceRole.ADMIN.value,
                "У вас нет прав на удаление участников",
            )

        # Удаление участника
        await self.data_manager.remove_workspace_member(workspace_id, user_id)

        self.logger.info(
            "Пользователь %s (ID: %s) удалил участника (ID: %s) из рабочего пространства %s",
            current_user.username, current_user.id, user_id, workspace_id
        )

        return WorkspaceMemberRemoveResponseSchema()

    async def check_workspace_access(
        self,
        workspace_id: int,
        user: CurrentUserSchema,
        required_role: WorkspaceRole = None
    ) -> bool:
        """
        Проверяет доступ пользователя к рабочему пространству.

        Args:
            workspace_id: ID рабочего пространства
            user: Текущий пользователь
            required_role: Требуемая роль (если None, проверяется только доступ)

        Returns:
            bool: True, если пользователь имеет доступ

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено
            WorkspaceAccessDeniedError: Если у пользователя нет доступа
        """
        workspace = await self.data_manager.get_workspace(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError(workspace_id)

        self.logger.debug(
            "Проверка доступа: пользователь %s (ID: %s) к рабочему пространству %s с требуемой ролью %s",
            user.username, user.id, workspace_id, required_role.value if required_role else "любая"
        )

        # Если роль не указана, проверяем только доступ
        if required_role is None:
            has_access = await self.data_manager.can_user_access_workspace(
                workspace_id, user.id
            )
            if not has_access:
                raise WorkspaceAccessDeniedError(workspace_id)
            return True

        # Если роль указана, проверяем права на управление
        can_manage = await self.data_manager.can_user_manage_workspace(
            workspace_id, user.id, required_role
        )
        if not can_manage:
            raise WorkspaceAccessDeniedError(
                workspace_id,
                required_role.value,
                f"У вас нет прав на выполнение этого действия (требуется роль {required_role.value})"
            )
        return True
