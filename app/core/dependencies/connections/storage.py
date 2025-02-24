from typing import Any
from aiologger import Logger
from aioboto3 import Session
from botocore.config import Config
from botocore.exceptions import ClientError
from dishka.integrations.fastapi import FromDishka
from app.core.settings import settings
from .base import BaseClient, BaseContextManager

class S3Client(BaseClient):
    """Клиент для работы с Amazon S3"""

    def __init__(self, logger: FromDishka[Logger], _settings: Any = settings) -> None:
        super().__init__(logger)
        self._s3_params = _settings.s3_params

    async def connect(self) -> Any:
        """Создает клиент S3"""
        s3_config = Config(s3={"addressing_style": "virtual"})
        try:
            await self._logger.debug("Создание клиента S3...")
            session = Session()
            self._client = await session.client(
                service_name="s3",
                config=s3_config,
                **self._s3_params
            )
            await self._logger.info("Клиент S3 успешно создан")
            return self._client
        except ClientError as e:
            error_details = e.response["Error"] if hasattr(e, "response") else "Нет деталей"
            await self._logger.error(
                "Ошибка создания S3 клиента: %s\nДетали: %s",
                e, error_details
            )
            raise

    async def close(self) -> None:
        """Закрывает клиент S3"""
        if self._client:
            await self._logger.debug("Закрытие клиента S3...")
            self._client = None
            await self._logger.info("Клиент S3 закрыт")

class S3ContextManager(BaseContextManager):
    """Контекстный менеджер для S3"""

    def __init__(self, logger: FromDishka[Logger]) -> None:
        super().__init__(logger)
        self.s3_client = S3Client(logger)

    async def connect(self) -> Any:
        return await self.s3_client.connect()

    async def close(self) -> None:
        await self.s3_client.close()
