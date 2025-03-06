from typing import List
from fastapi import FastAPI
from contextlib import asynccontextmanager


class ApplicationLifecycle:
    """Управление жизненным циклом приложения"""
    
    def __init__(self):
        from app.core.connections.base import BaseClient
        self.clients: List[BaseClient] = []

    async def startup(self, app: FastAPI):
        
        from app.core.connections.cache import RedisClient
        from app.core.connections.messaging import RabbitMQClient
        """Инициализация сервисов"""
        # Инициализируем клиентов
        self.clients = [
            RedisClient(),
            RabbitMQClient()
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер жизненного цикла"""
    lifecycle = ApplicationLifecycle()
    await lifecycle.startup(app)
    yield
    await lifecycle.shutdown(app)
