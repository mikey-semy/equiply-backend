from typing import Any, List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserExistsError, UserNotFoundError
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
        add_user: Добавление пользователя в БД
        get_user_by_email: Получение пользователя по email
        get_user_by_phone: Получение пользователя по телефону
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
                message=f"Пользователь с id {user_id} не найден",
                extra={"user_id": user_id},
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
                message=f"Пользователь с id {user_id} не найден",
                extra={"user_id": user_id},
            )

        updated_user = found_user_model
        updated_user.role = role
        return await self.update_one(found_user_model, updated_user)

    async def add_user(self, user: UserModel) -> UserModel:
        """
        Добавляет нового пользователя в базу данных.

        Args:
            user: Пользователь для добавления.

        Returns:
            UserCredentialsSchema: Данные пользователя.
        """
        try:
            return await self.add_one(user)
        except IntegrityError as e:
            if "users.email" in str(e):
                self.logger.error(
                    "add_user: Пользователь с email '%s' уже существует", user.email
                )
                raise UserExistsError("email", user.email) from e
            elif "users.phone" in str(e):
                self.logger.error(
                    "add_user: Пользователь с телефоном '%s' уже существует", user.phone
                )
                raise UserExistsError("phone", user.phone) from e
            else:
                self.logger.error("Ошибка при добавлении пользователя: %s", e)
                raise

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

    async def exists_user_with_role(self, user_id: int, role: str) -> bool:
        """
        Проверяет, существует ли пользователь с указанным ID и ролью.

        Args:
            user_id (int): ID пользователя
            role (str): Роль пользователя
        Returns:
            bool: True, если пользователья существует, иначе False
        """
        statement = select(self.model).where(
            self.model.id == user_id, self.model.role == role
        )
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

    async def get_user_by_email(self, email: str) -> UserCredentialsSchema | None:
        """
        Получает пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            UserCredentialsSchema | None: Данные пользователя или None.

        """
        statement = select(self.model).where(self.model.email == email)
        user = await self.get_one(statement)
        return user

    async def get_user_by_phone(self, phone: str) -> UserCredentialsSchema | None:
        """
        Получает пользователя по номеру телефона

        Args:
            phone: Номер телефона пользователя.

        Returns:
            UserCredentialsSchema | None: Данные пользователя или None.
        """
        statement = select(self.model).where(self.model.phone == phone)
        user = await self.get_one(statement)
        return user

    async def get_user_by_field(
        self, field: str, value: Any
    ) -> UserCredentialsSchema | None:
        """
        Получает пользователя по полю.

        Args:
            field: Поле пользователя.
            value: Значение поля пользователя.

        Returns:
            UserCredentialsSchema | None: Данные пользователя или None.
        """
        statement = select(self.model).where(getattr(self.model, field) == value)
        data = await self.get_one(statement)
        self.logger.debug("data: %s", data)
        return data

    async def get_users_by_field(self, field: str, value: Any) -> list[UserSchema]:
        """
        Получает список пользователей по полю.

        Args:
            field: Поле пользователя.
            value: Значение поля пользователя.

        Returns:
            List[UserSchema]: Список данных пользователей.
        """
        statement = select(self.model).where(getattr(self.model, field) == value)
        data = await self.get_all(statement)
        return data

    async def update_user(self, user_id: int, data: dict) -> UserUpdateSchema:
        """
        Обновляет данные пользователя.

        Args:
            user_id: Идентификатор пользователя.
            data: Данные для обновления.

        Returns:
            UserUpdateSchema: Обновленные данные пользователя.
        """
        user = await self.get_one(user_id)

        updated_user = UserUpdateSchema(**data)

        return await self.update_one(user, updated_user)

    async def delete_user(self, user_id: int) -> bool:
        """
        Удаляет пользователя из базы данных.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            bool

        Note:
            #! Можно рассмотреть реализацию мягкого удаления.
        """
        return await self.delete_item(user_id)
