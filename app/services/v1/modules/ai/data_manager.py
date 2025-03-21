from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import AISettingsSchema
from app.services.v1.base import BaseEntityManager
from app.models import AISettingsModel

class AIDataManager(BaseEntityManager[AISettingsSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=AISettingsSchema, model=AISettingsModel)

    async def get_user_settings(self, user_id: int) -> AISettingsModel:
        """
        Получает настройки пользователя или создаёт их, если не существуют

        Args:
            user_id: Идентификатор пользователя

        Returns:
            AISettingsModel: Настройки пользователя
        """

        ai_settings, _ = await self.get_or_create(
            filters={"user_id": user_id}
        )
        return ai_settings
