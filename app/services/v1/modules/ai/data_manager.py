from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import and_, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIChatModel, AISettingsModel
from app.schemas import AISettingsSchema
from app.schemas.v1.modules.ai import AIChatSchema
from app.services.v1.base import BaseEntityManager


class AIDataManager(BaseEntityManager[AISettingsSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session, schema=AISettingsSchema, model=AISettingsModel
        )

    async def get_user_settings(self, user_id: int) -> AISettingsModel:
        """
        Получает настройки пользователя или создаёт их, если не существуют

        Args:
            user_id: Идентификатор пользователя

        Returns:
            AISettingsModel: Настройки пользователя
        """

        ai_settings, _ = await self.get_or_create(filters={"user_id": user_id})
        return ai_settings


class AIChatManager(BaseEntityManager[AIChatSchema]):
    """
    Менеджер данных для работы с чатами AI.
    """

    def __init__(self, session):
        super().__init__(session, AIChatSchema, AIChatModel)

    async def create_chat(
        self, user_id: int, title: str, description: Optional[str] = None
    ) -> AIChatSchema:
        """
        Создает новый чат для пользователя.

        Args:
            user_id: ID пользователя
            title: Название чата
            description: Описание чата

        Returns:
            AIChatSchema: Созданный чат
        """
        chat_id = str(uuid4())
        chat = AIChatModel(
            user_id=user_id, title=title, description=description, chat_id=chat_id
        )
        return await self.add_item(chat)

    async def get_user_chats(self, user_id: int) -> List[AIChatSchema]:
        """
        Получает список чатов пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            List[AIChatSchema]: Список чатов
        """
        statement = (
            select(AIChatModel)
            .where(and_(AIChatModel.user_id == user_id, AIChatModel.is_active == True))
            .order_by(desc(AIChatModel.last_message_at))
        )

        return await self.get_items(statement)

    async def get_chat(self, chat_id: str, user_id: int) -> Optional[AIChatSchema]:
        """
        Получает чат по ID.

        Args:
            chat_id: ID чата
            user_id: ID пользователя для проверки доступа

        Returns:
            Optional[AIChatSchema]: Чат или None
        """
        statement = select(AIChatModel).where(
            and_(
                AIChatModel.chat_id == chat_id,
                AIChatModel.user_id == user_id,
                AIChatModel.is_active == True,
            )
        )

        return await self.get_item_by_field("chat_id", chat_id)

    async def update_last_message_time(self, chat_id: str) -> bool:
        """
        Обновляет время последнего сообщения.

        Args:
            chat_id: ID чата

        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            chat = await self.get_model_by_field("chat_id", chat_id)
            if not chat:
                return False

            # Используем текущее время в UTC
            current_time = datetime.now(timezone.utc)
            await self.update_some(chat, {"last_message_at": current_time})
            return True
        except Exception as e:
            self.logger.error(
                f"Ошибка при обновлении времени последнего сообщения: {str(e)}"
            )
            return False
