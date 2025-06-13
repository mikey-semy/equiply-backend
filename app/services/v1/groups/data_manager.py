import uuid
from typing import List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.v1.groups import UserGroupMemberModel, UserGroupModel
from app.schemas.v1.groups.base import UserGroupMemberSchema, UserGroupSchema
from app.schemas.v1.pagination import PaginationParams
from app.services.v1.base import BaseEntityManager

class UserGroupManager(BaseEntityManager[UserGroupSchema]):
    """Менеджер данных для групп пользователей."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserGroupSchema, UserGroupModel)

    async def get_groups_paginated(
        self,
        pagination: PaginationParams,
        workspace_id: Optional[int] = None,
        name: Optional[str] = None,
    ) -> Tuple[List[UserGroupSchema], int]:
        """
        Получает список групп с пагинацией и фильтрацией.

        Args:
            pagination: Параметры пагинации
            workspace_id: ID рабочего пространства для фильтрации
            name: Поиск по названию группы

        Returns:
            Tuple[List[UserGroupSchema], int]: Список групп и общее количество
        """
        # Создаем базовый запрос
        statement = select(self.model)

        # Применяем фильтры
        conditions = []
        if workspace_id is not None:
            conditions.append(self.model.workspace_id == workspace_id)
        if name is not None:
            conditions.append(self.model.name.ilike(f"%{name}%"))

        if conditions:
            statement = statement.where(and_(*conditions))

        # Получаем пагинированные результаты
        return await self.get_paginated_items(statement, pagination)

    async def get_user_groups(self, user_id: uuid.UUID) -> List[UserGroupSchema]:
        """
        Получает список групп, в которых состоит пользователь.

        Args:
            user_id: ID пользователя

        Returns:
            List[UserGroupSchema]: Список групп
        """
        statement = (
            select(UserGroupModel)
            .join(
                UserGroupMemberModel,
                UserGroupModel.id == UserGroupMemberModel.group_id
            )
            .where(UserGroupMemberModel.user_id == user_id)
        )

        return await self.get_items(statement)


class UserGroupMemberManager(BaseEntityManager[UserGroupMemberSchema]):
    """Менеджер данных для членов групп."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserGroupMemberSchema, UserGroupMemberModel)

    async def get_group_members(self, group_id: int) -> List[UserGroupMemberSchema]:
        """
        Получает список членов группы.

        Args:
            group_id: ID группы

        Returns:
            List[UserGroupMemberSchema]: Список членов группы
        """
        statement = select(self.model).where(self.model.group_id == group_id)
        return await self.get_items(statement)

    async def is_user_in_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> bool:
        """
        Проверяет, состоит ли пользователь в группе.

        Args:
            user_id: ID пользователя
            group_id: ID группы

        Returns:
            bool: True, если пользователь состоит в группе
        """
        statement = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.group_id == group_id
            )
        )
        return await self.exists(statement)

    async def add_user_to_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> UserGroupMemberSchema:
        """
        Добавляет пользователя в группу.

        Args:
            user_id: ID пользователя
            group_id: ID группы

        Returns:
            UserGroupMemberSchema: Созданная запись о членстве
        """
        # Проверяем, не состоит ли пользователь уже в группе
        if await self.is_user_in_group(user_id, group_id):
            raise ValueError(f"Пользователь с ID {user_id} уже состоит в группе с ID {group_id}")

        # Создаем запись о членстве
        member = UserGroupMemberModel(user_id=user_id, group_id=group_id)
        return await self.add_item(member)

    async def remove_user_from_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> bool:
        """
        Удаляет пользователя из группы.

        Args:
            user_id: ID пользователя
            group_id: ID группы

        Returns:
            bool: True, если пользователь успешно удален из группы
        """
        statement = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.group_id == group_id
            )
        )

        member = await self.get_one(statement)
        if not member:
            raise ValueError(f"Пользователь с ID {user_id} не состоит в группе с ID {group_id}")

        return await self.delete_item(member.id)
