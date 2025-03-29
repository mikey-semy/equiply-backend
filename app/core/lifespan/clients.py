from typing import List
from fastapi import FastAPI

from app.core.lifespan.base import register_startup_handler, register_shutdown_handler
from app.core.connections.base import BaseClient

class ClientsManager(BaseClient):
    """Менеджер клиентов приложения"""

    def __init__(self):
        super().__init__()
        self.clients: List[BaseClient] = []

    async def connect(self) -> None:
        """Инициализирует и подключает все клиенты"""
        from app.core.connections.cache import RedisClient
        from app.core.connections.messaging import RabbitMQClient

        # Инициализируем клиентов
        self.clients = [RedisClient(), RabbitMQClient()]

        # Подключаем клиентов
        for client in self.clients:
            await client.connect()

        self.logger.info(f"Подключено {len(self.clients)} клиентов")

    async def close(self) -> None:
        """Закрывает все клиенты"""
        for client in self.clients:
            await client.close()

        self.logger.info(f"Закрыто {len(self.clients)} клиентов")

# Создаем единственный экземпляр менеджера клиентов
clients_manager = ClientsManager()

@register_startup_handler
async def initialize_clients(app: FastAPI):
    """Инициализация клиентов при старте приложения"""
    app.state.clients_manager = clients_manager
    await clients_manager.connect()

@register_shutdown_handler
async def close_clients(app: FastAPI):
    """Закрытие клиентов при остановке приложения"""
    # Закрываем клиентов
    await app.state.clients_manager.close()

    # Закрываем DI контейнер
    await app.state.dishka_container.close()
