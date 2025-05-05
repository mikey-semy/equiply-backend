from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.v1.access import PermissionType, ResourceType
from app.schemas import CurrentUserSchema, PaginationParams, Page
from app.schemas.v1.groups.base import UserGroupSchema
from app.schemas.v1.groups.requests import (AddUserToGroupRequestSchema,
                                           RemoveUserFromGroupRequestSchema,
                                           UserGroupCreateRequestSchema,
                                           UserGroupUpdateRequestSchema)
from app.schemas.v1.groups.responses import (UserGroupCreateResponseSchema,
                                            UserGroupDeleteResponseSchema,
                                            UserGroupListResponseSchema,
                                            UserGroupMemberResponseSchema,
                                            UserGroupMembersResponseSchema,
                                            UserGroupResponseSchema,
                                            UserGroupUpdateResponseSchema)
from app.services.v1.access.service import AccessControlService
from app.services.v1.base import BaseService
from app.services.v1.groups.data_manager import (UserGroupManager,
                                                UserGroupMemberManager)


class GroupService(BaseService):
    """Сервис для работы с группами пользователей."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.group_manager = UserGroupManager(session)
        self.member_manager = UserGroupMemberManager(session)
        self.access_service = AccessControlService(session)

    async def create_group(
        self, group_data: UserGroupCreateRequestSchema, current_user: CurrentUserSchema
    ) -> UserGroupCreateResponseSchema:
        """
        Создает новую группу пользователей.

        Args:
            group_data: Данные группы
            current_user: Текущий пользователь

        Returns:
            UserGroupCreateResponseSchema: Ответ с созданной группой
        """
        # Проверяем права на создание группы
        if group_data.workspace_id:
            await self.access_service.authorize(
                user_id=current_user.id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=group_data.workspace_id,
                permission=PermissionType.MANAGE,
            )

        # Создаем группу
        from app.models.v1.groups import UserGroupModel
        group_model = UserGroupModel(**group_data.model_dump())
        group = await self.group_manager.add_item(group_model)

        return UserGroupCreateResponseSchema(data=group)

    async def get_groups(
        self,
        pagination: PaginationParams,
        workspace_id: Optional[int] = None,
        name: Optional[str] = None,
        current_user: CurrentUserSchema = None,
    ) -> UserGroupListResponseSchema:
        """
        Получает список групп с пагинацией и фильтрацией.

        Args:
            pagination: Параметры пагинации
            workspace_id: ID рабочего пространства для фильтрации
            name: Поиск по названию группы
            current_user: Текущий пользователь

        Returns:
            UserGroupListResponseSchema: Ответ со списком групп
        """
        # Проверяем права на просмотр групп в рабочем пространстве
        if workspace_id:
            await self.access_service.authorize(
                user_id=current_user.id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=workspace_id,
                permission=PermissionType.READ,
            )

        # Получаем группы
        groups, total = await self.group_manager.get_groups_paginated(
            pagination=pagination,
            workspace_id=workspace_id,
            name=name,
        )

        # Формируем ответ с пагинацией
        page = Page(
            items=groups,
            total=total,
            page=pagination.page,
            size=pagination.limit,
        )

        return UserGroupListResponseSchema(data=page)

    async def get_group(
        self, group_id: int, current_user: CurrentUserSchema
    ) -> UserGroupResponseSchema:
        """
        Получает группу по ID.

        Args:
            group_id: ID группы
            current_user: Текущий пользователь

        Returns:
            UserGroupResponseSchema: Ответ с данными группы
        """
        # Получаем группу
        group = await self.group_manager.get_item_by_field("id", group_id)
        if not group:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        # Проверяем права на просмотр группы
        if group.workspace_id:
            await self.access_service.authorize(
                user_id=current_user.id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=group.workspace_id,
                permission=PermissionType.READ,
            )

        return UserGroupResponseSchema(data=group)

    async def update_group(
        self,
        group_id: int,
        group_data: UserGroupUpdateRequestSchema,
        current_user: CurrentUserSchema,
    ) -> UserGroupUpdateResponseSchema:
        """
        Обновляет группу.

        Args:
            group_id: ID группы
            group_data: Данные для обновления
            current_user: Текущий пользователь

        Returns:
            UserGroupUpdateResponseSchema: Ответ с обновленной группой
        """
        # Получаем группу
        group = await self.group_manager.get_item_by_field("id", group_id)
        if not group:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        # Проверяем права на обновление группы
        if group.workspace_id:
            await self.access_service.authorize(
                user_id=current_user.id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=group.workspace_id,
                permission=PermissionType.MANAGE,
            )

        # Обновляем группу
        update_data = group_data.model_dump(exclude_unset=True)
        updated_group = await self.group_manager.update_item(group_id, update_data)

        return UserGroupUpdateResponseSchema(data=updated_group)

    async def delete_group(
        self, group_id: int, current_user: CurrentUserSchema
    ) -> UserGroupDeleteResponseSchema:
        """
        Удаляет группу.

        Args:
            group_id: ID группы
            current_user: Текущий пользователь

        Returns:
            UserGroupDeleteResponseSchema: Ответ об успешном удалении
        """
        # Получаем группу
        group = await self.group_manager.get_item_by_field("id", group_id)
        if not group:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        # Проверяем права на удаление группы
        if group.workspace_id:
            await self.access_service.authorize(
                user_id=current_user.id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=group.workspace_id,
                permission=PermissionType.MANAGE,
            )

        # Удаляем группу
        await self.group_manager.delete_item(group_id)

        return UserGroupDeleteResponseSchema()

    async def get_group_members(
        self, group_id: int, current_user: CurrentUserSchema
    ) -> UserGroupMembersResponseSchema:
        """
        Получает список членов группы.

        Args:
            group_id: ID группы
            current_user: Текущий пользователь

        Returns:
            UserGroupMembersResponseSchema: Ответ со списком членов группы
        """
        # Получаем группу
        group = await self.group_manager.get_item_by_field("id", group_id)
        if not group:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        # Проверяем права на просмотр членов группы
        if group.workspace_id:
            await self.access_service.authorize(
                user_id=current_user.id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=group.workspace_id,
                permission=PermissionType.READ,
            )

        # Получаем членов группы
        members = await self.member_manager.get_group_members(group_id)

        return UserGroupMembersResponseSchema(data=members)

    async def add_user_to_group(
        self,
        group_id: int,
        request: AddUserToGroupRequestSchema,
        current_user: CurrentUserSchema,
    ) -> UserGroupMemberResponseSchema:
        """
        Добавляет пользователя в группу.

        Args:
            group_id: ID группы
            request: Данные запроса
            current_user: Текущий пользователь

        Returns:
            UserGroupMemberResponseSchema: Ответ с данными о членстве
        """
        # Получаем группу
        group = await self.group_manager.get_item_by_field("id", group_id)
        if not group:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        # Проверяем права на управление группой
        if group.workspace_id:
            await self.access_service.authorize(
                user_id=current_user.id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=group.workspace_id,
                permission=PermissionType.MANAGE,
            )

        # Добавляем пользователя в группу
        member = await self.member_manager.add_user_to_group(
            user_id=request.user_id,
            group_id=group_id,
        )

        return UserGroupMemberResponseSchema(data=member)

    async def remove_user_from_group(
        self,
        group_id: int,
        request: RemoveUserFromGroupRequestSchema,
        current_user: CurrentUserSchema,
    ) -> UserGroupDeleteResponseSchema:
        """
        Удаляет пользователя из группы.

        Args:
            group_id: ID группы
            request: Данные запроса
            current_user: Текущий пользователь

        Returns:
            UserGroupDeleteResponseSchema: Ответ об успешном удалении
        """
        # Получаем группу
        group = await self.group_manager.get_item_by_field("id", group_id)
        if not group:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        # Проверяем права на управление группой
        if group.workspace_id:
            await self.access_service.authorize(
                user_id=current_user.id,
                resource_type=ResourceType.WORKSPACE,
                resource_id=group.workspace_id,
                permission=PermissionType.MANAGE,
            )

        # Удаляем пользователя из группы
        await self.member_manager.remove_user_from_group(
            user_id=request.user_id,
            group_id=group_id,
        )

        return UserGroupDeleteResponseSchema(message="Пользователь успешно удален из группы")

    async def get_user_groups(
        self, user_id: int, current_user: CurrentUserSchema
    ) -> List[UserGroupSchema]:
        """
        Получает список групп, в которых состоит пользователь.

        Args:
            user_id: ID пользователя
            current_user: Текущий пользователь

        Returns:
            List[UserGroupSchema]: Список групп
        """
        # Проверяем права на просмотр групп пользователя
        if current_user.id != user_id:
            # Если текущий пользователь не тот, чьи группы запрашиваются,
            # то нужны права администратора
            from app.models.v1.users import UserRole
            if current_user.role != UserRole.ADMIN:
                raise ValueError("Недостаточно прав для просмотра групп другого пользователя")

        # Получаем группы пользователя
        return await self.group_manager.get_user_groups(user_id)
