from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas import UserSchema
from app.services.v1.base import BaseEntityManager


class ProfileDataManager(BaseEntityManager[UserSchema]):
    """
    Класс для работы с данными пользователей в базе данных.

    Args:
        session: Асинхронная сессия для работы с базой данных.
        schema: Схема данных пользователя.
        model: Модель данных пользователя.

    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def get_avatar(self, user_id: int) -> str:
        """
        Получает аватар пользователя.

        Args:
            user_id (int): ID пользователя.
        Returns:
            ProfileSchema: Профиль пользователя.
        """
        profile = await self.get_item(user_id)
        return profile.avatar if profile else ""

    async def update_avatar(self, user_id: int, avatar_url: str) -> ProfileSchema:
        """
        Обновляет аватар пользователя в БД.

        Args:
            user_id: ID пользователя
            avatar_url: URL аватара в S3
        Returns:
            ProfileSchema: Обновленный профиль
        """
        profile = await self.get_item(user_id)
        profile_dict = profile.to_dict()
        profile_dict['avatar'] = await avatar_url
        updated_profile = ProfileSchema(**profile_dict)
        return await self.update_item(user_id, updated_profile)