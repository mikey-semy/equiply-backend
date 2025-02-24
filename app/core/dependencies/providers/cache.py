from typing import AsyncGenerator
from aiologger import Logger
from redis import Redis
from dishka import Provider, provide, Scope
from app.core.dependencies.connections.cache import RedisClient

class RedisProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_client(self, logger: Logger) -> AsyncGenerator[Redis, None]:
        client = RedisClient(logger)
        redis = await client.connect()
        yield redis
        await client.close()
