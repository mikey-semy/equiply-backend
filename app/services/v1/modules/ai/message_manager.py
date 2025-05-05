from datetime import datetime
from typing import List

from sqlalchemy import and_, select

from app.models.v1.modules.ai import AIMessageModel, ModelType
from app.schemas import MessageSchema
from app.services.v1.base import BaseEntityManager


class AIMessageManager(BaseEntityManager):
    """
    Менеджер данных для работы с сообщениями чата AI.
    """

    def __init__(self, session):
        super().__init__(session, MessageSchema, AIMessageModel)

    async def save_chat_messages(self, user_id: int, chat_id: str, messages: List[MessageSchema]) -> bool:
        """
        Сохраняет сообщения чата в базу данных.

        Args:
            user_id: ID пользователя
            chat_id: ID чата
            messages: Список сообщений

        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            # Удаляем существующие сообщения для этого чата
            await self.delete_chat_messages(user_id, chat_id)

            # Создаем новые модели сообщений
            message_models = []
            for msg in messages:
                # Определяем тип модели, если указан
                model_type = None
                if hasattr(msg, 'model') and msg.model:
                    try:
                        model_type = ModelType(msg.model)
                    except ValueError:
                        model_type = ModelType.CUSTOM

                message_model = AIMessageModel(
                    user_id=user_id,
                    chat_id=chat_id,
                    role=msg.role,
                    text=msg.text,
                    model_type=model_type,
                    timestamp=datetime.now()
                )
                message_models.append(message_model)

            # Сохраняем все сообщения
            await self.bulk_create(message_models)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении сообщений чата: %s", str(e))
            return False

    async def get_chat_messages(self, user_id: int, chat_id: str) -> List[MessageSchema]:
        """
        Получает сообщения чата из базы данных.

        Args:
            user_id: ID пользователя
            chat_id: ID чата

        Returns:
            List[MessageSchema]: Список сообщений
        """
        try:
            statement = (
                select(AIMessageModel)
                .where(
                    and_(
                        AIMessageModel.user_id == user_id,
                        AIMessageModel.chat_id == chat_id
                    )
                )
                .order_by(AIMessageModel.timestamp)
            )

            models = await self.get_all(statement)

            # Преобразуем модели в схемы
            messages = []
            for model in models:
                message = MessageSchema(
                    role=model.role,
                    text=model.text
                )
                if model.model_type:
                    message.model = model.model_type.value
                messages.append(message)

            return messages
        except Exception as e:
            self.logger.error("Ошибка при получении сообщений чата: %s", str(e))
            return []

    async def delete_chat_messages(self, user_id: int, chat_id: str) -> bool:
        """
        Удаляет сообщения чата из базы данных.

        Args:
            user_id: ID пользователя
            chat_id: ID чата

        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            statement = (
                select(AIMessageModel)
                .where(
                    and_(
                        AIMessageModel.user_id == user_id,
                        AIMessageModel.chat_id == chat_id
                    )
                )
            )

            models = await self.get_all(statement)

            for model in models:
                await self.delete_item(model.id)

            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении сообщений чата: %s", str(e))
            return False
