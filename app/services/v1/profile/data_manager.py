from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas import AvatarDataSchema, ProfileSchema
from app.services.v1.base import BaseEntityManager


class ProfileDataManager(BaseEntityManager[ProfileSchema]):
    """
    Класс для работы с данными пользователей в базе данных.

    Args:
        session: Асинхронная сессия для работы с базой данных.
        schema: Схема данных пользователя.
        model: Модель данных пользователя.

    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=ProfileSchema, model=UserModel)

    async def get_avatar(self, user_id: int) -> AvatarDataSchema:
        """
        Получает аватар пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            AvatarDataSchema: Данные аватара пользователя.
        """
        user = await self.get_item(user_id)
        if not user:
            self.logger.warning(
                "Пользователь с ID %s не найден при получении аватара", user_id
            )
            return AvatarDataSchema(url="", alt="Аватар не найден")

        return AvatarDataSchema(
            url=user.avatar or "", alt=f"Аватар пользователя {user.username}"
        )

    async def update_avatar(self, user_id: int, avatar_url: str) -> AvatarDataSchema:
        """
        Обновляет аватар пользователя в БД.

        Args:
            user_id: ID пользователя
            avatar_url: URL аватара в S3

        Returns:
            AvatarDataSchema: Обновленные данные аватара
        """
        # Получаем пользователя
        user = await self.get_item(user_id)
        if not user:
            self.logger.error(
                "Пользователь с ID %s не найден при обновлении аватара", user_id
            )
            raise ValueError(f"Пользователь с ID {user_id} не найден")

        # Обновляем только поле аватара
        try:
            await self.update_items(user_id, {"avatar": avatar_url})

        except (ValueError, SQLAlchemyError):
            self.logger.error("Не удалось обновить аватар для пользователя %s", user_id)
            raise RuntimeError(f"Не удалось обновить аватар для пользователя {user_id}")

        # Получаем обновленного пользователя и возвращаем данные аватара
        updated_user = await self.get_item(user_id)

        return AvatarDataSchema(
            url=updated_user.avatar, alt=f"Аватар пользователя {updated_user.username}"
        )
