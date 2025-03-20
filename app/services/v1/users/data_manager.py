from typing import List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas import (PaginationParams, UserCredentialsSchema, UserRole,
                         UserSchema)
from app.services.v1.base import BaseEntityManager


class UserDataManager(BaseEntityManager[UserSchema]):
    """
    Менеджер данных для работы с пользователями в БД.

    Реализует низкоуровневые операции для работы с таблицей пользователей.
    Обрабатывает исключения БД и преобразует их в доменные исключения.

    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[UserSchema]): Схема сериализации данных
        model (Type[UserModel]): Модель пользователя

    Methods:
        toggle_active: Изменение статуса активности пользователя
        assign_role: Назначение роли пользователю
        get_user: Получение пользователя по id
        get_users: Получение списка пользователей
        delete_user: Удаление пользователя

    Raises:
        UserNotFoundError: Когда пользователь не найден
        UserExistsError: При попытке создать дубликат пользователя
        IntegrityError: При нарушении целостности данных
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def toggle_active(self, user_id: int, is_active: bool) -> UserModel:
        """
        Изменяет статус активности пользователя.

        Args:
            user_id (int): Идентификатор пользователя
            is_active (bool): Статус активности

        Returns:
            UserModel: Обновленная модель пользователя
        """
        found_user_model = await self.get_user(user_id)

        if not found_user_model:
            return None

        updated_user = found_user_model
        updated_user.is_active = is_active

        return await self.update_one(found_user_model, updated_user)

    async def assign_role(self, user_id: int, role: UserRole) -> UserModel:
        """
        Назначает роль пользователю.

        Args:
            user_id (int): Идентификатор пользователя.
            role (str): Роль пользователя.

        Returns:
            UserModel: Обновленная модель пользователя
        """
        found_user_model = await self.get_user(user_id)

        if not found_user_model:
            return None

        updated_user = found_user_model
        updated_user.role = role

        return await self.update_one(found_user_model, updated_user)

    async def get_user(self, user_id: int) -> UserCredentialsSchema | None:
        """
        Получает пользователя по id.

        Args:
            user_id: ID пользователя.

        Returns:
            UserCredentialsSchema | None: Данные пользователя или None.
        """
        statement = select(self.model).where(self.model.id == user_id)
        user = await self.get_one(statement)
        return user

    async def get_users(
        self,
        pagination: PaginationParams,
        role: UserRole = None,
        search: str = None,
    ) -> tuple[List[UserSchema], int]:
        """
        Получает список пользователей с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination (PaginationParams): Параметры пагинации
            role (UserRole): Фильтрация по роли пользователя
            search (str): Поиск по тексту пользователя

        Returns:
            tuple[List[UserSchema], int]: Список пользователей и их общее количество
        """
        statement = select(self.model).distinct()

        # Поиск по тексту (имя пользователя или email)
        if search:
            statement = statement.filter(
                or_(
                    self.model.username.ilike(f"%{search}%"),
                    self.model.email.ilike(f"%{search}%")
                )
            )

        # Фильтр по роли пользователя
        if role:
            statement = statement.filter(self.model.role == role)

        return await self.get_paginated_items(statement, pagination)

    async def delete_user(self, user_id: int) -> bool:
        """
        Удаляет пользователя из базы данных.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            bool
        """
        return await self.delete_item(user_id)
