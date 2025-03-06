from redis import Redis, from_url
from app.core.settings import settings, Config
from .base import BaseClient, BaseContextManager


class RedisClient(BaseClient):
    """Клиент для работы с Redis"""

    def __init__(self, _settings: Config = settings) -> None:
        super().__init__()
        self._redis_params = _settings.redis_params

    async def connect(self) -> Redis:
        """Создает подключение к Redis"""
        self.logger.debug("Подключение к Redis...")
        self._client = from_url(**self._redis_params)
        self.logger.info("Подключение к Redis установлено")
        return self._client

    async def close(self) -> None:
        """Закрывает подключение к Redis"""
        if self._client:
            self.logger.debug("Закрытие подключения к Redis...")
            self._client.close()
            self._client = None
            self.logger.info("Подключение к Redis закрыто")

class RedisContextManager(BaseContextManager):
    """Контекстный менеджер для Redis"""

    def __init__(self) -> None:
        super().__init__()
        self.redis_client = RedisClient()

    async def connect(self) -> Redis:
        return await self.redis_client.connect()

    async def close(self) -> None:
        await self.redis_client.close()
