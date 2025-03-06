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
