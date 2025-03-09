from typing import AsyncGenerator
from redis import Redis
from dishka import Provider, provide, Scope
from app.core.connections.cache import RedisClient

class RedisProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_client(self) -> AsyncGenerator[Redis, None]:
        client = RedisClient()
        redis = await client.connect()
        yield redis
        await client.close()

class RedisMiddlewareProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_middleware_client(self) -> Redis:
        client = RedisClient()
        redis = await client.connect()
        # Не закрываем соединение, т.к. оно должно жить все время работы приложения
        return redis