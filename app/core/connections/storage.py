from typing import Any

from aioboto3 import Session
from botocore.config import Config as BotocoreConfig
from botocore.exceptions import ClientError

from app.core.settings import Config as AppConfig
from app.core.settings import settings

from .base import BaseClient, BaseContextManager


class S3Client(BaseClient):
    """Клиент для работы с Amazon S3"""

    def __init__(self, _settings: AppConfig = settings) -> None:
        super().__init__()
        self._s3_params = _settings.s3_params

    async def connect(self) -> Any:
        """Создает клиент S3"""
        s3_config = BotocoreConfig(s3={"addressing_style": "virtual"})
        try:
            self.logger.debug("Создание клиента S3...")
            session = Session()
            self._client = await session.client(
                service_name="s3", config=s3_config, **self._s3_params
            )
            self.logger.info("Клиент S3 успешно создан")
            return self._client
        except ClientError as e:
            error_details = (
                e.response["Error"] if hasattr(e, "response") else "Нет деталей"
            )
            self.logger.error(
                "Ошибка создания S3 клиента: %s\nДетали: %s", e, error_details
            )
            raise

    async def close(self) -> None:
        """Закрывает клиент S3"""
        if self._client:
            self.logger.debug("Закрытие клиента S3...")
            self._client = None
            self.logger.info("Клиент S3 закрыт")


class S3ContextManager(BaseContextManager):
    """Контекстный менеджер для S3"""

    def __init__(self) -> None:
        super().__init__()
        self.s3_client = S3Client()

    async def connect(self) -> Any:
        return await self.s3_client.connect()

    async def close(self) -> None:
        await self.s3_client.close()
