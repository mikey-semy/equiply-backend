import json
from typing import List

from app.core.exceptions import AIHistoryNotFoundError
from app.schemas import MessageSchema

from .base import BaseRedisDataManager


class AIRedisStorage(BaseRedisDataManager):
    """
    Redis хранилище для истории чата с AI
    """

    async def get_chat_history(self, user_id: int, chat_id: str) -> List[MessageSchema]:
        """
        Получает историю чата из Redis.

        Args:
            user_id: ID пользователя
            chat_id: ID чата

        Returns:
            List[MessageSchema]: Список сообщений

        Raises:
            AIHistoryNotFoundError: При ошибке получения истории чата
        """
        key = f"chat:{user_id}:{chat_id}"
        self.logger.debug("Пытаемся получить историю чата по ключу: %s", key)
        try:
            history = await self.get(key)
            self.logger.debug("Получены данные из Redis: %s", history)
            if not history:
                self.logger.debug("История чата пуста для ключа: %s", key)
                return []
            messages_data = json.loads(history)
            self.logger.debug("Десериализованные данные: %s", messages_data)

            result = [MessageSchema.model_validate(msg) for msg in messages_data]
            self.logger.debug("Валидированные сообщения: %d шт.", len(result))
            return result
        except json.JSONDecodeError as e:
            self.logger.error("Ошибка декодирования JSON: %s, данные: %s", str(e), history)
            raise AIHistoryNotFoundError(f"Некорректный формат данных истории чата: {str(e)}") from e
        except Exception as e:
            self.logger.error("Ошибка при получении истории чата: %s", str(e))
            raise AIHistoryNotFoundError(f"Не удалось получить историю чата: {str(e)}") from e

    async def save_chat_history(
        self, user_id: int, chat_id: str, messages: List[MessageSchema]
    ) -> None:
        """
        Сохраняет историю чата в Redis.

        Args:
            user_id: ID пользователя
            chat_id: ID чата
            messages: Список сообщений

        Raises:
            Exception: При ошибке сохранения истории чата
        """
        key = f"chat:{user_id}:{chat_id}"
        messages_json = json.dumps([msg.model_dump() for msg in messages])
        await self.set(key, messages_json, expires=3600)  # Храним 1 час

    async def clear_chat_history(self, user_id: int, chat_id: str) -> bool:
        """
        Очищает историю чата в Redis.

        Args:
            user_id: ID пользователя
            chat_id: ID чата

        Returns:
            bool: True, если история чата была очищена, иначе False

        Raises:
            Exception: При ошибке очистки истории чата
        """
        key = f"chat:{user_id}:{chat_id}"
        await self.delete(key)

        if not await self.get(key):
            return True
        return False
