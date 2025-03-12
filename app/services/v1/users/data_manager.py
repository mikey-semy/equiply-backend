from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundError
from app.models import UserModel
from app.schemas import (PaginationParams, UserCredentialsSchema, UserRole,
                         UserSchema, UserUpdateSchema)
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
        exists_user: Проверка наличия пользователя по id
        get_user: Получение пользователя по id
        get_users: Получение списка пользователей
        update_user: Обновление данных пользователя
        delete_user: Удаление пользователя

    Raises:
        UserNotFoundError: Когда пользователь не найден
        UserExistsError: При попытке создать дубликат пользователя
        IntegrityError: При нарушении целостности данных
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def toggle_active(self, user_id: int, is_active: bool) -> UserUpdateSchema:
        """
        Изменяет статус активности пользователя.

        Args:
            user_id (int): Идентификатор пользователя
            is_active (bool): Статус активности

        Returns:
            UserUpdateSchema: Данные пользователя с обновленным статусом
        """
        found_user_model = await self.get_user(user_id)

        if not found_user_model:
            raise UserNotFoundError(
                field="id",
                value=str(user_id)
            )

        updated_user = found_user_model
        updated_user.is_active = is_active
        return await self.update_one(found_user_model, updated_user)

    async def assign_role(self, user_id: int, role: UserRole) -> UserUpdateSchema:
        """
        Назначает роль пользователю.

        Args:
            user_id (int): Идентификатор пользователя.
            role (str): Роль пользователя.

        Returns:
            UserUpdateSchema: Данные пользователя с обновленной ролью.
        """
        found_user_model = await self.get_user(user_id)

        if not found_user_model:
            raise UserNotFoundError(
                field="id",
                value=str(user_id)
            )

        updated_user = found_user_model
        updated_user.role = role
        return await self.update_one(found_user_model, updated_user)

    async def exists_user(self, user_id: int) -> bool:
        """
        Проверяет, существует ли пользователь с указанным ID.

         Args:
             user_id (int): ID пользователя

         Returns:
             bool: True, если пользователья существует, иначе False
        """
        statement = select(self.model).where(self.model.id == user_id)
        return await self.exists(statement)

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

        # Поиск по тексту
        if search:
            statement = statement.filter(self.model.text.ilike(f"%{search}%"))

        # Фильтр по роли пользователя
        if role:
            statement = statement.filter(self.model.role == role)

        return await self.get_paginated(statement, pagination)


    async def update_user(self, user_id: int, data: dict) -> UserUpdateSchema:
        """
        Обновляет данные пользователя.

        Args:
            user_id: Идентификатор пользователя.
            data: Данные для обновления.

        Returns:
            UserUpdateSchema: Обновленные данные пользователя.
        """
        user = await self.get_item(user_id)

        updated_user = UserUpdateSchema(**data)

        return await self.update_item(user, updated_user)

    async def delete_user(self, user_id: int) -> bool:
        """
        Удаляет пользователя из базы данных.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            bool
        """
        return await self.delete_item(user_id)
