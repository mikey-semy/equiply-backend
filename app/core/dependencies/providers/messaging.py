from typing import AsyncGenerator

from aio_pika import Connection
from dishka import Provider, Scope, provide

from app.core.connections.messaging import RabbitMQClient


class RabbitMQProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_client(self) -> AsyncGenerator[Connection, None]:
        client = RabbitMQClient()
        connection = await client.connect()
        yield connection
        await client.close()
