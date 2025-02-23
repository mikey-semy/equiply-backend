"""
Модуль для работы с Amazon S3 с использованием aioboto3.

Этот модуль предоставляет классы и функции для управления сессиями S3,
создания асинхронных клиентов и обработки ошибок.

Основные компоненты:
- S3Client: Класс для настройки и создания асинхронного клиента S3.
- SessionContextManager: Контекстный менеджер для управления жизненным циклом сессий S3.
- get_s3_session: Асинхронный генератор для получения сессии S3.

Модуль использует асинхронные возможности aioboto3 для эффективной работы с S3
в асинхронных приложениях.
"""
from typing import Any
from aiologger import Logger
from aioboto3 import Session
from botocore.config import Config
from botocore.exceptions import ClientError
from dishka.integrations.fastapi import FromDishka
from app.core.settings import settings


class S3Client:
    """
    Класс для управления сессией S3 с использованием aioboto3.
    """

    def __init__(
        self,
        logger: FromDishka[Logger],
        _settings: Any = settings
    ) -> None:
        """
        Инициализирует экземпляр S3Client.

        Args:
            logger (FromDishka[Logger]): Логгер для записи сообщений.
            settings (Any): Объект конфигурации.
        """
        self._s3_params = _settings.s3_params
        self.logger = logger

    async def create_async_session_factory(self) -> Any:
        """
        Создание асинхронного клиента S3.

        Returns:
            Any: Асинхронный клиент S3.

        Raises:
            ClientError: Если возникла ошибка при создании клиента.
        """
        s3_config = Config(s3={"addressing_style": "virtual"})
        try:
            session = Session()
            async with session.client(
                service_name="s3",
                config=s3_config,
                **self._s3_params
            ) as client:
                self.logger.info("Клиент S3 успешно создан")
                return client
        except ClientError as e:
            self.logger.error(
                "Ошибка создания S3 клиента: %s\nДетали: %s",
                e,
                e.response["Error"] if hasattr(e, "response") else "Нет деталей",
            )
            self.logger.error("❌ Ошибка при создании клиента S3: %s", e)
            raise


class SessionContextManager:
    """
    Контекстный менеджер для управления сессиями S3.
    """

    def __init__(self, logger: FromDishka[Logger]):
        """
        Инициализирует экземпляр SessionContextManager.
        """
        self.s3_session = S3Client(logger=logger)
        self._client = None

    async def __aenter__(self):
        """
        Вход в контекстный менеджер.

        Returns:
            SessionContextManager: Экземпляр SessionContextManager с активной сессией S3.
        """
        self._client = await self.s3_session.create_async_session_factory()
        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Выход из контекстного менеджера.

        Args:
            exc_type: Тип исключения, если оно возникло.
            exc_val: Значение исключения, если оно возникло.
            exc_tb: Объект трассировки, если исключение возникло.
        """
        await self.close_client()

    async def close_client(self):
        """
        Закрытие клиента S3.

        Обнуляет ссылку на сессию, чтобы освободить ресурсы.
        """
        if self._client:
            self._client = None
