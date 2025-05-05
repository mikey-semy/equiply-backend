import enum
import logging
from abc import ABC, abstractmethod
from typing import List

from app.core.integrations.cache.ai import AIRedisStorage

from app.schemas import MessageSchema


class StorageType(str, enum.Enum):
    """Типы хранилищ для истории чатов"""
    REDIS = "redis"
    DATABASE = "database"
    HYBRID = "hybrid"

logger = logging.getLogger(__name__)

class BaseAIStorage(ABC):
    """Базовый класс для хранилища истории чатов"""

    @abstractmethod
    async def get_chat_history(self, user_id: int, chat_id: str) -> List[MessageSchema]:
        """Получает историю чата"""
        pass

    @abstractmethod
    async def save_chat_history(self, user_id: int, chat_id: str, messages: List[MessageSchema]) -> None:
        """Сохраняет историю чата"""
        pass

    @abstractmethod
    async def clear_chat_history(self, user_id: int, chat_id: str) -> bool:
        """Очищает историю чата"""
        pass


class RedisAIStorage(BaseAIStorage):
    """Хранилище истории чатов в Redis"""

    def __init__(self, redis_storage: AIRedisStorage):
        self.storage = redis_storage

    async def get_chat_history(self, user_id: int, chat_id: str) -> List[MessageSchema]:
        logger.debug("Получение истории чата из Redis: user_id=%s, chat_id=%s", user_id, chat_id)
        return await self.storage.get_chat_history(user_id, chat_id)

    async def save_chat_history(self, user_id: int, chat_id: str, messages: List[MessageSchema]) -> None:
        logger.debug("Сохранение истории чата в Redis: user_id=%s, chat_id=%s, сообщений: %s", user_id, chat_id, len(messages))
        await self.storage.save_chat_history(user_id, chat_id, messages)

    async def clear_chat_history(self, user_id: int, chat_id: str) -> bool:
        logger.debug("Очистка истории чата в Redis: user_id=%s, chat_id=%s", user_id, chat_id)
        return await self.storage.clear_chat_history(user_id, chat_id)


class DatabaseAIStorage(BaseAIStorage):
    """Хранилище истории чатов в базе данных"""

    def __init__(self, session):
        from app.services.v1.modules.ai.message_manager import AIMessageManager
        self.manager = AIMessageManager(session)

    async def get_chat_history(self, user_id: int, chat_id: str) -> List[MessageSchema]:
        logger.debug("Получение истории чата из БД: user_id=%s, chat_id=%s", user_id, chat_id)
        messages = await self.manager.get_chat_messages(user_id, chat_id)
        if not messages:
            logger.debug("История чата в БД не найдена: user_id=%s, chat_id=%s", user_id, chat_id)
            return []
        logger.debug("Получено сообщений из БД: %s", len(messages))
        return messages

    async def save_chat_history(self, user_id: int, chat_id: str, messages: List[MessageSchema]) -> None:
        logger.debug("Сохранение истории чата в БД: user_id=%s, chat_id=%s, сообщений: %s", user_id, chat_id, len(messages))
        await self.manager.save_chat_messages(user_id, chat_id, messages)

    async def clear_chat_history(self, user_id: int, chat_id: str) -> bool:
        logger.debug("Очистка истории чата в БД: user_id=%s, chat_id=%s", user_id, chat_id)
        return await self.manager.delete_chat_messages(user_id, chat_id)


class HybridAIStorage(BaseAIStorage):
    """Гибридное хранилище истории чатов (Redis + БД)"""

    def __init__(self, redis_storage: AIRedisStorage, session):
        self.redis = RedisAIStorage(redis_storage)
        self.db = DatabaseAIStorage(session)

    async def get_chat_history(self, user_id: int, chat_id: str) -> List[MessageSchema]:
        logger.debug("Получение истории чата из гибридного хранилища: user_id=%s, chat_id=%s", user_id, chat_id)
        # Сначала пробуем получить из Redis (быстрее)
        try:
            messages = await self.redis.get_chat_history(user_id, chat_id)
            if messages:
                logger.debug("История чата найдена в Redis: user_id=%s, chat_id=%s, сообщений: %s", user_id, chat_id, len(messages))
                return messages
        except Exception as e:
            logger.warning("Ошибка при получении истории из Redis: %s", str(e))

        # Если в Redis нет или была ошибка, берем из БД
        messages = await self.db.get_chat_history(user_id, chat_id)

        # Если нашли в БД, кэшируем в Redis для будущих запросов
        if messages:
            logger.debug("История чата найдена в БД: user_id=%s, chat_id=%s, сообщений: %s", user_id, chat_id, len(messages))
            try:
                await self.redis.save_chat_history(user_id, chat_id, messages)
                logger.debug("История чата из БД кэширована в Redis: user_id=%s, chat_id=%s", user_id, chat_id)
            except Exception as e:
                logger.warning("Ошибка при кэшировании истории в Redis: %s", str(e))
        else:
            logger.debug("История чата не найдена ни в Redis, ни в БД: user_id=%s, chat_id=%s", user_id, chat_id)

        return messages

    async def save_chat_history(self, user_id: int, chat_id: str, messages: List[MessageSchema]) -> None:
        logger.debug("Сохранение истории чата в гибридное хранилище: user_id=%s, chat_id=%s, сообщений: %s", user_id, chat_id, len(messages))
        # Сохраняем и в Redis, и в БД
        try:
            await self.redis.save_chat_history(user_id, chat_id, messages)
            logger.debug("История чата сохранена в Redis: user_id=%s, chat_id=%s", user_id, chat_id)
        except Exception as e:
            logger.warning("Ошибка при сохранении истории в Redis: %s", str(e))

        # В любом случае сохраняем в БД
        await self.db.save_chat_history(user_id, chat_id, messages)
        logger.debug("История чата сохранена в БД: user_id=%s, chat_id=%s", user_id, chat_id)

    async def clear_chat_history(self, user_id: int, chat_id: str) -> bool:
        logger.debug("Очистка истории чата в гибридном хранилище: user_id=%s, chat_id=%s", user_id, chat_id)
        # Очищаем и в Redis, и в БД
        redis_success = True
        try:
            redis_success = await self.redis.clear_chat_history(user_id, chat_id)
            logger.debug("История чата в Redis очищена: user_id=%s, chat_id=%s, успех: %s", user_id, chat_id, redis_success)
        except Exception as e:
            logger.warning("Ошибка при очистке истории в Redis: %s", str(e))
            redis_success = False

        db_success = await self.db.clear_chat_history(user_id, chat_id)
        logger.debug("История чата в БД очищена: user_id=%s, chat_id=%s, успех: %s", user_id, chat_id, db_success)

        # Успешно, если хотя бы одно хранилище очищено
        return redis_success or db_success


def get_ai_storage(storage_type: str, redis_storage: AIRedisStorage, session) -> BaseAIStorage:
    """
    Фабричный метод для создания хранилища нужного типа

    Args:
        storage_type: Тип хранилища
        redis_storage: Экземпляр Redis хранилища
        session: Сессия базы данных

    Returns:
        BaseAIStorage: Хранилище нужного типа
    """
    try:
        storage_enum = StorageType(storage_type)
        logger.info("Инициализация хранилища истории чатов типа: %s", storage_enum.value)
    except ValueError:
        storage_enum = StorageType.REDIS
        logger.warning("Неизвестный тип хранилища: %s, используется Redis", storage_type)

    if storage_enum == StorageType.REDIS:
        return RedisAIStorage(redis_storage)
    elif storage_enum == StorageType.DATABASE:
        return DatabaseAIStorage(session)
    elif storage_enum == StorageType.HYBRID:
        return HybridAIStorage(redis_storage, session)
    else:
        # По умолчанию используем Redis
        return RedisAIStorage(redis_storage)