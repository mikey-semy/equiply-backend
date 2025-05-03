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

from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UserNotFoundError
from app.core.integrations.cache.auth import AuthRedisDataManager
from app.schemas import (CurrentUserSchema, PaginationParams,
                         UserActiveUpdateResponseSchema,
                         UserDeleteResponseSchema, UserDetailDataSchema,
                         UserRole, UserRoleUpdateResponseSchema, UserSchema,
                         UserStatusDataSchema, UserStatusResponseSchema)
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
        get_users Получает список пользователей с возможностью пагинации, поиска и фильтрации.
        delete_user: Удаление пользователя
        get_user_status: Получает статус пользователя
    """

    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(session)
        self.data_manager = UserDataManager(session)
        self.redis_data_manager = AuthRedisDataManager(redis)

    async def toggle_active(
        self, user_id: int, is_active: bool, current_user: CurrentUserSchema
    ) -> UserActiveUpdateResponseSchema:
        """
        Назначает роль пользователю.

        Args:
            user_id (int): Идентификатор пользователя
            role (UserRole): Роль пользователя
            current_user (CurrentUserSchema): Текущий авторизованный пользователь

        Returns:
            UserActiveUpdateResponseSchema: Схема ответа с обновленными данными пользователя

        Raises:
            ForbiddenError: Если у текущего пользователя недостаточно прав для изменения роли
            UserNotFoundError: Если пользователь с указанным ID не найден
        """
        # Проверка прав доступа - только админы и модераторы могут блокировать/разблокировать
        allowed_roles = [UserRole.ADMIN, UserRole.MODERATOR]
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                detail="Только администраторы и модераторы могут блокировать/разблокировать пользователей",
                required_role=f"{UserRole.ADMIN.value} или {UserRole.MODERATOR.value}",
            )

        # Проверка, что пользователь не блокирует сам себя
        if user_id == current_user.id:
            raise ForbiddenError(
                detail="Нельзя изменить статус активности своей учетной записи"
            )

        # Получаем пользователя, которому меняем статус
        target_user = await self.data_manager.get_item_by_field("id", user_id)
        if not target_user:
            raise UserNotFoundError(field="id", value=user_id)

        # Проверка иерархии ролей - модератор не может блокировать админа
        if current_user.role == UserRole.MODERATOR and target_user.role in [
            UserRole.ADMIN
        ]:
            raise ForbiddenError(
                detail=f"Модератор не может блокировать пользователя с ролью {target_user.role}"
            )

        # Вызываем метод менеджера данных для обновления статуса
        updated_user = await self.data_manager.toggle_active(user_id, is_active)

        # Дополнительная проверка на случай, если что-то пошло не так
        if not updated_user:
            raise UserNotFoundError(field="id", value=user_id)

        # Логирование действия
        action = "разблокирован" if is_active else "заблокирован"
        self.logger.info(
            f"Пользователь {target_user.username} (ID: {user_id}) {action} пользователем {current_user.username} (ID: {current_user.id})"
        )

        # Формируем сообщение в зависимости от действия
        message = (
            f"Пользователь успешно {'разблокирован' if is_active else 'заблокирован'}"
        )

        # Преобразуем модель пользователя в схему UserDetailDataSchema
        user_data = UserDetailDataSchema(
            id=updated_user.id,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            username=updated_user.username,
            email=updated_user.email,
            role=updated_user.role,
            is_active=updated_user.is_active,
        )

        # Возвращаем схему ответа
        return UserActiveUpdateResponseSchema(message=message, data=user_data)

    async def assign_role(
        self, user_id: int, role: UserRole, current_user: CurrentUserSchema
    ) -> UserRoleUpdateResponseSchema:
        """
        Назначает роль пользователю.

        Args:
            user_id (int): Идентификатор пользователя
            role (UserRole): Роль пользователя
            current_user (CurrentUserSchema): Текущий авторизованный пользователь

        Returns:
            UserRoleUpdateResponseSchema: Схема ответа с обновленными данными пользователя

        Raises:
            ForbiddenError: Если у текущего пользователя недостаточно прав для изменения роли
            UserNotFoundError: Если пользователь с указанным ID не найден
        """
        # Проверяем, что текущий пользователь имеет роль администратора
        allowed_roles = [UserRole.ADMIN]
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                detail="Только администраторы могут изменять роли пользователей",
                required_role=f"{UserRole.ADMIN.value}",
            )

        # Проверяем, что пользователь не пытается изменить свою собственную роль
        if user_id == current_user.id:
            raise ForbiddenError(detail="Нельзя изменить свою собственную роль")

        # Получаем пользователя, которому меняем роль
        target_user = await self.data_manager.get_item_by_field("id", user_id)
        if not target_user:
            raise UserNotFoundError(field="id", value=user_id)

        # Проверяем, что текущий пользователь не пытается изменить роль пользователя с более высокой ролью
        # ADMIN > MODERATOR > USER
        role_hierarchy = {UserRole.ADMIN: 3, UserRole.MODERATOR: 2, UserRole.USER: 1}

        if role_hierarchy.get(target_user.role, 0) > role_hierarchy.get(
            current_user.role, 0
        ):
            raise ForbiddenError(
                detail=f"Нельзя изменить роль пользователя с более высокой ролью ({target_user.role})"
            )

        # Проверяем, что пользователь не пытается назначить роль выше своей
        if role_hierarchy.get(role, 0) > role_hierarchy.get(current_user.role, 0):
            raise ForbiddenError(detail=f"Нельзя назначить роль выше своей ({role})")

        # Вызываем метод менеджера данных для обновления роли
        updated_user = await self.data_manager.assign_role(user_id, role)

        # Дополнительная проверка на случай, если что-то пошло не так
        if not updated_user:
            raise UserNotFoundError(field="id", value=user_id)

        # Логирование действия
        self.logger.info(
            "Пользователю %s (ID: %s) назначена роль %s пользователем %s (ID: %s)",
            target_user.username,
            user_id,
            role,
            current_user.username,
            current_user.id,
        )

        # Преобразуем модель пользователя в схему UserDetailDataSchema
        user_data = UserDetailDataSchema(
            id=updated_user.id,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            username=updated_user.username,
            email=updated_user.email,
            role=updated_user.role,
            is_active=updated_user.is_active,
        )

        # Возвращаем схему ответа
        return UserRoleUpdateResponseSchema(
            message=f"Пользователю успешно назначена роль {role.value}", data=user_data
        )

    async def get_users(
        self,
        pagination: PaginationParams,
        role: UserRole = None,
        search: str = None,
        current_user: CurrentUserSchema = None,
    ) -> tuple[List[UserSchema], int]:
        """
        Получает список пользователей с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination (PaginationParams): Параметры пагинации
            role (UserRole): Фильтрация по роли пользователя
            search (str): Поиск по тексту пользователя
            current_user (CurrentUserSchema): Текущий авторизованный пользователь

        Returns:
            tuple[List[UserSchema], int]: Список пользователей и общее количество пользователей.

        Raises:
            ForbiddenError: Если у пользователя недостаточно прав для просмотра списка пользователей
        """
        allowed_roles = [UserRole.ADMIN, UserRole.MODERATOR, UserRole.USER]
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                detail="Только администраторы и модераторы могут просматривать список пользователей",
                required_role=f"{UserRole.ADMIN.value} или {UserRole.MODERATOR.value}",
            )

        if current_user.role == UserRole.USER:
            if role == UserRole.ADMIN and current_user.role != UserRole.ADMIN:
                raise ForbiddenError(
                    detail="У вас недостаточно прав для просмотра администраторов",
                    required_role=UserRole.ADMIN.value,
                )

        self.logger.info(
            f"Пользователь {current_user.username} (ID: {current_user.id}) запросил список пользователей. "
            f"Параметры: пагинация={pagination}, роль={role}, поиск='{search}'"
        )

        users, total = await self.data_manager.get_users(
            pagination=pagination,
            role=role,
            search=search,
        )

        for user in users:
            user.is_online = await self.redis_data_manager.get_online_status(user.id)

        return users, total

    async def get_user_status(self, user_id: int) -> UserStatusResponseSchema:
        """
        Получает статус пользователя

        Args:
            user_id: Идентификатор пользователя

        Returns:
            UserStatusResponseSchema: Статус пользователя

        Raises:
            UserNotFoundError: Если пользователь не найден
        """
        # Получаем пользователя из БД
        user = await self.data_manager.get_item_by_field("id", user_id)
        if not user:
            raise UserNotFoundError(
                field="id",
                value=user_id,
            )

        # Получаем онлайн статус напрямую
        is_online = await self.redis_data_manager.get_online_status(user_id)

        # Получаем последнюю активность из сессий
        tokens = await self.redis_data_manager.get_user_sessions(user.email)
        last_activity = max(
            [
                await self.redis_data_manager.get_last_activity(token)
                for token in tokens
            ],
            default=0,
        )

        return UserStatusResponseSchema(
            data=UserStatusDataSchema(is_online=is_online, last_activity=last_activity)
        )

    async def delete_user(
        self, user_id: int, current_user: CurrentUserSchema
    ) -> UserDeleteResponseSchema:
        """
        Удаляет пользователя из базы данных.

        Args:
            user_id: Идентификатор пользователя.
            current_user: Текущий авторизованный пользователь.

        Returns:
            UserDeleteResponseSchema: Схема ответа с сообщением об успешном удалении.

        Raises:
            ForbiddenError: Если у текущего пользователя недостаточно прав для удаления
            UserNotFoundError: Если пользователь с указанным ID не найден
        """
        # Проверка прав доступа - только админы могут удалять пользователей
        if current_user.role != UserRole.ADMIN:
            raise ForbiddenError(
                detail="Только администраторы могут удалять пользователей",
                required_role=UserRole.ADMIN.value,
            )

        # Проверка, что пользователь не пытается удалить сам себя
        if user_id == current_user.id:
            raise ForbiddenError(
                detail="Нельзя удалить свою собственную учетную запись"
            )

        # Получаем пользователя, которого удаляем
        target_user = await self.data_manager.get_item_by_field("id", user_id)
        if not target_user:
            raise UserNotFoundError(field="id", value=user_id)

        # Удаляем пользователя
        await self.data_manager.delete_user(user_id)

        # Логирование действия
        self.logger.info(
            f"Пользователь {target_user.username} (ID: {user_id}) удален пользователем {current_user.username} (ID: {current_user.id})"
        )

        # Возвращаем схему ответа
        return UserDeleteResponseSchema()
