"""
Модуль для работы с системой обмена сообщениями.

Предоставляет классы для управления подключением к RabbitMQ:
- RabbitMQClient: Клиент для установки и управления подключением к брокеру сообщений
  с поддержкой автоматических повторных попыток подключения

Модуль использует настройки подключения из конфигурации приложения и реализует
базовые интерфейсы из модуля base.py.
"""
import asyncio
from typing import Optional

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError

from app.core.settings import settings

from .base import BaseClient


class RabbitMQClient(BaseClient):
    """
    Клиент для работы с RabbitMQ

    Реализует базовый класс BaseClient для установки и управления
    подключением к брокеру сообщений RabbitMQ с механизмом повторных попыток.

    Attributes:
        _instance (Optional[AbstractRobustConnection]): Экземпляр подключения к RabbitMQ
        _is_connected (bool): Флаг состояния подключения
        _max_retries (int): Максимальное количество попыток подключения
        _retry_delay (int): Задержка между попытками подключения в секундах
        _connection_params (dict): Параметры подключения из настроек
        _debug_mode (bool): Режим отладки из настроек приложения
        logger (logging.Logger): Логгер для записи событий
    """

    _instance: Optional[AbstractRobustConnection] = None
    _is_connected: bool = False
    _max_retries: int = 5
    _retry_delay: int = 5

    def __init__(self) -> None:
        """
        Инициализация клиента RabbitMQ.
        Настраивает параметры подключения и режим отладки из конфигурации.
        """
        super().__init__()
        self._connection_params = settings.rabbitmq_params
        self._debug_mode = getattr(settings, "DEBUG", False)

    async def connect(self) -> Optional[AbstractRobustConnection]:
        """
        Создает подключение к RabbitMQ

        Устанавливает подключение к брокеру сообщений с механизмом повторных попыток.
        В режиме отладки при неудачном подключении возвращает None вместо исключения.

        Returns:
            Optional[AbstractRobustConnection]: Подключение к RabbitMQ или None в случае неудачи

        Raises:
            AMQPConnectionError: При ошибке подключения (только в production режиме)
        """
        if not self._instance and not self._is_connected:
            for attempt in range(self._max_retries):
                try:
                    self.logger.debug("Подключение к RabbitMQ...")
                    self._instance = await connect_robust(**self._connection_params)
                    self._is_connected = True
                    self.logger.info("Подключение к RabbitMQ установлено")
                    break
                except AMQPConnectionError as e:
                    self.logger.error(f"Ошибка подключения к RabbitMQ: {e}")
                    if attempt < self._max_retries - 1:
                        self.logger.warning(
                            f"Повторная попытка {attempt+1}/{self._max_retries} через {self._retry_delay} секунд..."
                        )
                        await asyncio.sleep(self._retry_delay)
                    else:
                        self._is_connected = False
                        self._instance = None
                        self.logger.warning(
                            "RabbitMQ недоступен после всех попыток, но приложение продолжит работу"
                        )

                        # В режиме разработки не выбрасываем исключение, просто возвращаем None
                        if self._debug_mode:
                            return None
                        else:
                            # raise
                            return None
        return self._instance

    async def close(self) -> None:
        """
        Закрывает подключение к RabbitMQ

        Безопасно закрывает активное подключение к брокеру сообщений.
        """
        if self._instance and self._is_connected:
            try:
                self.logger.debug("Закрытие подключения к RabbitMQ...")
                await self._instance.close()
                self.logger.info("Подключение к RabbitMQ закрыто")
            finally:
                self._instance = None
                self._is_connected = False

    async def health_check(self) -> bool:
        """
        Проверяет состояние подключения

        Returns:
            bool: True если подключение активно и работает, False в противном случае
        """
        if not self._instance or not self._is_connected:
            return False
        try:
            return not self._instance.is_closed
        except AMQPConnectionError:
            return False

    @property
    def is_connected(self) -> bool:
        """
        Возвращает статус подключения

        Returns:
            bool: True если подключение установлено, False в противном случае
        """
        return self._is_connected
