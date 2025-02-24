from typing import AsyncGenerator
from aiologger import Logger
from aio_pika import Connection
from dishka import Provider, provide, Scope
from app.core.dependencies.connections.messaging import RabbitMQClient

class RabbitMQProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_client(self, logger: Logger) -> AsyncGenerator[Connection, None]:
        client = RabbitMQClient(logger)
        connection = await client.connect()
        yield connection
        await client.close()
