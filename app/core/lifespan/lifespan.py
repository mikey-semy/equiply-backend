from typing import List
from fastapi import FastAPI
from contextlib import asynccontextmanager


class ApplicationLifecycle:
    """Управление жизненным циклом приложения"""
    
    def __init__(self):
        from app.core.dependencies.connections.base import BaseClient
        self.logger = None
        self.clients: List[BaseClient] = []

    async def startup(self, app: FastAPI):
        
        from app.core.dependencies.connections.logger import LoggerClient
        from app.core.dependencies.connections.cache import RedisClient
        from app.core.dependencies.connections.messaging import RabbitMQClient
        """Инициализация сервисов"""
        # Инициализируем логгер первым
        self.logger = await LoggerClient.get_instance()

        # Инициализируем клиентов
        self.clients = [
            RedisClient(self.logger),
            RabbitMQClient(self.logger)
        ]

        # Подключаем клиентов
        for client in self.clients:
            await client.connect()

    async def shutdown(self, app: FastAPI):
        """Закрытие сервисов"""
        # Закрываем клиентов
        for client in self.clients:
            await client.close()

        # Закрываем DI контейнер
        await app.state.dishka_container.close()

        # Закрываем логгер последним
        await self.logger.shutdown()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер жизненного цикла"""
    lifecycle = ApplicationLifecycle()
    await lifecycle.startup(app)
    yield
    await lifecycle.shutdown(app)
