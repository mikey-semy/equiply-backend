from typing import AsyncGenerator
from redis import Redis
from dishka import Provider, provide, Scope
from app.core.dependencies.connections.messaging import RabbitMQClient

class RabbitMQProvider(Provider):
    """
    Провайдер для RabbitMQ клиента.
    """
    @provide(scope=Scope.REQUEST)
    async def get_client(self) -> AsyncGenerator[Redis, None]:
        """
        Возвращает RabbitMQ клиент.

        Yields:
            AsyncGenerator[Redis, None]: RabbitMQ клиент.
        """
        connection = await RabbitMQClient.get_instance()
        if connection and await RabbitMQClient.health_check():
            yield connection
            await RabbitMQClient.close()
