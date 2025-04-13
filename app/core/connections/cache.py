"""
Модуль для работы с Redis.

Предоставляет классы для управления подключением к Redis:
- RedisClient: Клиент для установки и управления подключением к Redis
- RedisContextManager: Контекстный менеджер для автоматического управления подключением

Redis используется в приложении как универсальное хранилище данных в памяти,
поддерживающее различные структуры данных и паттерны использования.

Модуль использует настройки подключения из конфигурации приложения и реализует
базовые интерфейсы из модуля base.py.
"""

from redis import Redis, from_url

from app.core.settings import Config, settings

from .base import BaseClient, BaseContextManager


class RedisClient(BaseClient):
    """
    Клиент для работы с Redis

    Реализует базовый класс BaseClient для установки и управления
    подключением к Redis серверу.

    Attributes:
        _redis_params (dict): Параметры подключения к Redis из конфигурации
        _client (Optional[Redis]): Экземпляр подключения к Redis
        logger (logging.Logger): Логгер для записи событий подключения
    """

    def __init__(self, _settings: Config = settings) -> None:
        """
        Инициализация клиента Redis.

        Args:
            _settings (Config): Конфигурация приложения с параметрами подключения к Redis.
                              По умолчанию использует глобальные настройки приложения.
        """
        super().__init__()
        self._redis_params = _settings.redis_params

    async def connect(self) -> Redis:
        """Создает подключение к Redis

        Устанавливает соединение с Redis сервером, используя параметры
        из конфигурации приложения.

        Returns:
            Redis: Экземпляр подключенного Redis клиента

        Raises:
            RedisError: При ошибке подключения к Redis серверу
        """
        self.logger.debug("Подключение к Redis...")
        self._client = from_url(**self._redis_params)
        self.logger.info("Подключение к Redis установлено")
        return self._client

    async def close(self) -> None:
        """
        Закрывает подключение к Redis

        Корректно завершает соединение с Redis сервером и очищает
        ссылку на клиент. Безопасно обрабатывает случай, когда
        подключение уже закрыто.
        """
        if self._client:
            self.logger.debug("Закрытие подключения к Redis...")
            self._client.close()
            self._client = None
            self.logger.info("Подключение к Redis закрыто")


class RedisContextManager(BaseContextManager):
    """
    Контекстный менеджер для Redis

    Реализует контекстный менеджер для автоматического управления
    жизненным циклом подключения к Redis.

    Attributes:
        redis_client (RedisClient): Экземпляр клиента Redis
        _client (Optional[Redis]): Ссылка на активное подключение
        logger (logging.Logger): Логгер для записи событий
    """

    def __init__(self) -> None:
        """
        Инициализация контекстного менеджера.
        Создает экземпляр RedisClient для управления подключением.
        """
        super().__init__()
        self.redis_client = RedisClient()

    async def connect(self) -> Redis:
        """
        Создает подключение к Redis

        Делегирует создание подключения экземпляру RedisClient.

        Returns:
            Redis: Экземпляр подключенного Redis клиента
        """
        return await self.redis_client.connect()

    async def close(self) -> None:
        """
        Закрывает подключение к Redis

        Делегирует закрытие подключения экземпляру RedisClient.
        """
        await self.redis_client.close()
