"""
Модуль для работы с пользователями.

Этот модуль содержит основные классы для управления пользователями в системе:
- UserService: Сервисный слой для бизнес-логики работы с пользователями
- UserDataManager: Слой доступа к данным для работы с БД

Основные операции:
- Создание пользователей
- Получение пользователей по email
- Обновление данных пользователей
- Удаление пользователей

Пример использования:
    service = UserService(session)
    user = await service.create_user(user_data)
    user_by_email = await service.get_user_by_email("test@test.com")
"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from app.core.exceptions import UserNotFoundError
from app.core.integrations.cache.auth import AuthRedisStorage
from app.schemas import (PaginationParams, UserCredentialsSchema, UserRole,
                         UserSchema, UserStatusResponseSchema,
                         UserUpdateSchema)
from app.services.v1.base import BaseService
from app.services.v1.users.data_manager import UserDataManager


class UserService(BaseService):
    """
    Сервис для управления пользователями.

    Предоставляет высокоуровневые методы для работы с пользователями,
    инкапсулируя бизнес-логику и взаимодействие с базой данных.

    Attributes:
        session (AsyncSession): Асинхронная сессия для работы с БД
        redis: Redis ...
    
    Methods:
        toggle_active: Изменяет статус активности пользователя (бан). 
        assign_role: Назначает роль пользователю.
        exists_user: Проверка наличия пользователя по id
        get_users Получает список пользователей с возможностью пагинации, поиска и фильтрации.
        update_user: Обновление данных пользователя
        delete_user: Удаление пользователя
        get_user_status: Получает статус пользователя
    """

    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(session)
        self._data_manager = UserDataManager(session)
        self._redis_storage = AuthRedisStorage(redis)

    async def toggle_active(self, user_id: int, is_active: bool) -> UserUpdateSchema:
        """
        Изменяет статус активности пользователя.

        Args:
            user_id (int): Идентификатор пользователя
            is_active (bool): Статус активности

        Returns:
            UserUpdateSchema: Обновленный пользователь
        """
        return await self._data_manager.toggle_active(user_id, is_active)

    async def assign_role(self, user_id: int, role: UserRole) -> UserUpdateSchema:
        """
        Назначает роль пользователю.

        Args:
            user_id (int): Идентификатор пользователя
            role (UserRole): Роль пользователя

        Returns:
            UserUpdateSchema: Обновленный пользователь
        """
        return await self._data_manager.assign_role(user_id, role)

    async def exists_user(self, user_id: int) -> bool:
        """
        Проверяет существует ли пользователь с указанным id.

        Args:
            user_id: Идентификатор пользователя

        Returns:
            bool: True, если пользователь существует, False - иначе
        """
        return await self._data_manager.exists_user(user_id)

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
            tuple[List[FeedbackSchema], int]: Список пользователей и общее количество пользователей.
        """
        return await self._data_manager.get_users(
            pagination=pagination,
            role=role,
            search=search,
        )

    async def update_user(self, user_id: int, data: dict) -> UserCredentialsSchema:
        """
        Обновляет данные пользователя.

        Args:
            user_id: Идентификатор пользователя.
            data: Данные для обновления.

        Returns:
            UserCredentialsSchema: Обновленные данные пользователя.
        """
        return await self._data_manager.update_user(user_id, data)

    async def delete_user(self, user_id: int) -> None:
        """
        Удаляет пользователя из базы данных.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            None
        """
        return await self._data_manager.delete_user(user_id)

    async def get_user_status(self, user_id: int) -> UserStatusResponseSchema:
        """
        Получает статус пользователя
        """
        # Получаем пользователя из БД
        user = await self._data_manager.get_item_by_field("id", user_id)
        if not user:
            raise UserNotFoundError(
                field="id",
                value=user_id,
            )

        # Получаем онлайн статус напрямую
        is_online = await self._redis_storage.get_online_status(user_id)

        # Получаем последнюю активность из сессий
        tokens = await self._redis_storage.get_user_sessions(user.email)
        last_activity = max(
            [await self._redis_storage.get_last_activity(token) for token in tokens],
            default=0,
        )

        return UserStatusResponseSchema(
            is_online=is_online, last_activity=last_activity
        )
