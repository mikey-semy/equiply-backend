import re
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas import UserSchema
from app.services.v1.base import BaseEntityManager


class AuthDataManager(BaseEntityManager[UserSchema]):
    """
    Класс для работы с данными пользователей в базе данных.

    Args:
        session: Асинхронная сессия для работы с базой данных.
        schema: Схема данных пользователя.
        model: Модель данных пользователя.

    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def get_user_by_identifier(self, identifier: str) -> Optional[UserModel]:
        """
        Получение пользователя по имени пользователя, email или телефону.

        Args:
            identifier: Имя пользователя, email или телефон.

        Returns:
            Пользователь или None, если пользователь не найден.
        """
        # Проверяем, является ли identifier email-ом
        if '@' in identifier:
            user = await self.get_user_by_field("email", identifier)
            if user:
                return user

        # Проверяем, является ли identifier телефоном
        # Паттерн для телефона в формате +7 (XXX) XXX-XX-XX
        phone_pattern = r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$"
        if re.match(phone_pattern, identifier):
            user = await self.get_user_by_field("phone", identifier)
            if user:
                return user

        # В противном случае, ищем по имени пользователя
        user = await self.get_user_by_field("username", identifier)
        if user:
            return user

        # Если ничего не найдено, возвращаем None
        return None

    async def update_online_status(self, user_id: int, is_online: bool) -> None:
        """
        Обновляет онлайн статус пользователя
        """
        await self.update_fields(
            user_id,
            {
                "is_online": is_online,
                "last_seen": datetime.now(timezone.utc) if not is_online else None,
            },
        )

    async def update_last_seen(self, user_id: int) -> None:
        """
        Обновляет время последнего визита
        """
        await self.update_fields(user_id, {"last_seen": datetime.now(timezone.utc)})

    async def get_all_users(self) -> List[UserModel]:
        """
        Получает список всех пользователей.
        """
        statement = select(self.model)
        return await self.get_items(statement)
