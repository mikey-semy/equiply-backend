"""
Модуль для работы с облачным хранилищем.

Предоставляет классы для управления подключением к облачному хранилищу (S3-совместимому):
- S3Client: Клиент для установки и управления подключением к S3
- S3ContextManager: Контекстный менеджер для автоматического управления подключением

Модуль использует настройки подключения из конфигурации приложения и реализует
базовые интерфейсы из модуля base.py.
"""

from typing import Any

from aioboto3 import Session
from botocore.config import Config as BotocoreConfig
from botocore.exceptions import ClientError

from app.core.settings import Config as AppConfig
from app.core.settings import settings

from .base import BaseClient, BaseContextManager


class S3Client(BaseClient):
    """
    Клиент для работы с Amazon S3

    Реализует базовый класс BaseClient для установки и управления
    подключением к S3-совместимому хранилищу.

    Attributes:
        settings (AppConfig): Конфигурация приложения с параметрами подключения к S3
        session (Session | None): Сессия AWS для работы с S3
        client (Any | None): Клиент S3
        client_context (Any | None): Контекст клиента S3
        logger (logging.Logger): Логгер для записи событий подключения
    """

    def __init__(self, settings: AppConfig = settings) -> None:
        """
        Инициализация клиента S3.

        Args:
            settings (AppConfig): Конфигурация приложения с параметрами подключения.
                                По умолчанию использует глобальные настройки приложения.
        """
        super().__init__()
        self.settings = settings
        self.session = None
        self.client = None

    async def connect(self) -> Any:
        """Создает клиент S3

        Устанавливает соединение с S3-совместимым хранилищем, используя параметры
        из конфигурации приложения.

        Returns:
            Any: Контекст клиента S3 для выполнения операций с хранилищем

        Raises:
            ClientError: При ошибке подключения к S3
        """
        s3_config = BotocoreConfig(s3={"addressing_style": "virtual"})
        try:
            self.logger.debug("Создание клиента S3...")
            self.session = Session(
                aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID.get_secret_value(),
                aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
                region_name=self.settings.AWS_REGION,
            )
            client_context = self.session.client(
                service_name=self.settings.AWS_SERVICE_NAME,
                endpoint_url=self.settings.AWS_ENDPOINT,
                config=s3_config,
            )
            self.client_context = client_context
            self.logger.info("Клиент S3 успешно создан")
            return client_context
        except ClientError as e:
            error_details = (
                e.response["Error"] if hasattr(e, "response") else "Нет деталей"
            )
            self.logger.error(
                "Ошибка создания S3 клиента: %s\nДетали: %s", e, error_details
            )
            raise

    async def close(self) -> None:
        """
        Закрывает клиент S3

        Освобождает ресурсы, связанные с клиентом S3.
        Безопасно обрабатывает случай, когда клиент уже закрыт.
        """
        if self.client:
            self.logger.debug("Закрытие клиента S3...")
            self.client = None
            self.logger.info("Клиент S3 закрыт")


class S3ContextManager(BaseContextManager):
    """
    Контекстный менеджер для S3

    Реализует контекстный менеджер для автоматического управления
    жизненным циклом подключения к S3-хранилищу.

    Attributes:
        s3_client (S3Client): Клиент S3 для управления подключением
        client (Any | None): Активный клиент S3
        client_context (Any | None): Контекст клиента S3
        logger (logging.Logger): Логгер для записи событий
    """

    def __init__(self) -> None:
        """
        Инициализация контекстного менеджера.
        Создает экземпляр S3Client для управления подключением.
        """
        super().__init__()
        self.s3_client = S3Client()
        self.client = None
        self.client_context = None

    async def __aenter__(self):
        """
        Асинхронный вход в контекст.

        Returns:
            Any: Активный клиент S3 для работы с хранилищем
        """
        self.client_context = await self.s3_client.connect()

        self.client = await self.client_context.__aenter__()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Асинхронный выход из контекста.

        Args:
            exc_type: Тип исключения, если оно произошло
            exc_val: Экземпляр исключения, если оно произошло
            exc_tb: Трейсбек исключения, если оно произошло
        """
        if self.client_context:
            await self.client_context.__aexit__(exc_type, exc_val, exc_tb)
        await self.s3_client.close()

    async def connect(self) -> Any:
        """
        Устанавливает подключение к S3.

        Returns:
            Any: Контекст клиента S3
        """
        return await self.s3_client.connect()

    async def close(self) -> None:
        """
        Закрывает подключение к S3.
        """
        await self.s3_client.close()
