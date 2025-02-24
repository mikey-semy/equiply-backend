from typing import Optional
import asyncio
from aiologger import Logger
from aio_pika import Connection, connect_robust
from aio_pika.exceptions import AMQPConnectionError
from app.core.settings import settings
from .base import BaseClient

class RabbitMQClient(BaseClient):
    """Клиент для работы с RabbitMQ"""

    _instance: Optional[Connection] = None
    _is_connected: bool = False
    _max_retries: int = 5
    _retry_delay: int = 5

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)
        self._connection_params = settings.rabbitmq_params

    async def connect(self) -> Connection:
        """Создает подключение к RabbitMQ"""
        if not self._instance and not self._is_connected:
            for attempt in range(self._max_retries):
                try:
                    await self._logger.debug("Подключение к RabbitMQ...")
                    self._instance = await connect_robust(**self._connection_params)
                    self._is_connected = True
                    await self._logger.info("Подключение к RabbitMQ установлено")
                    break
                except AMQPConnectionError as e:
                    await self._logger.error(f"Ошибка подключения к RabbitMQ: {e}")
                    if attempt < self._max_retries - 1:
                        await asyncio.sleep(self._retry_delay)
                    else:
                        self._is_connected = False
                        self._instance = None
                        raise
        return self._instance

    async def close(self) -> None:
        """Закрывает подключение к RabbitMQ"""
        if self._instance and self._is_connected:
            try:
                await self._logger.debug("Закрытие подключения к RabbitMQ...")
                await self._instance.close()
                await self._logger.info("Подключение к RabbitMQ закрыто")
            finally:
                self._instance = None
                self._is_connected = False

    async def health_check(self) -> bool:
        """Проверяет состояние подключения"""
        if not self._instance or not self._is_connected:
            return False
        try:
            return not self._instance.is_closed
        except AMQPConnectionError:
            return False

    @property
    def is_connected(self) -> bool:
        """Возвращает статус подключения"""
        return self._is_connected
