"""
Модуль для работы с Redis.

"""

from redis import Redis, from_url

from app.core.settings import settings


class RedisClient:
    """
    Синглтон для подключения к Redis.

    Attributes:
        _instance: Экземпляр Redis.
    """

    _instance: Redis = None

    @classmethod
    async def get_instance(cls) -> Redis:
        """
        Возвращает экземпляр Redis.

        Returns:
            Экземпляр Redis.
        """
        if not cls._instance:
            cls._instance = from_url(
                **settings.redis_params
            )
        return cls._instance

    @classmethod
    async def close(cls):
        """
        Закрывает подключение к Redis.

        Returns:
            None
        """
        if cls._instance:
            cls._instance.close()
            cls._instance = None
