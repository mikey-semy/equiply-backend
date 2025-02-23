from typing import AsyncGenerator
from redis import Redis
from dishka import Provider, provide, Scope
from app.core.dependencies.connections.cache import RedisClient

class RedisProvider(Provider):
    """
    Провайдер для Redis клиента.

    Attributes:
        redis (Redis): Клиент Redis.

    Methods:
        get_client: Возвращает Redis клиент.
    """
    @provide(scope=Scope.REQUEST)
    async def get_client(self) -> AsyncGenerator[Redis, None]:
        """
        Возвращает Redis клиент.

        Yields:
            AsyncGenerator[Redis, None]: Redis клиент.
        """
        redis = await RedisClient.get_instance()
        yield redis
        await RedisClient.close()
