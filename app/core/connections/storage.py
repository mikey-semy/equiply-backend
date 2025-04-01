from typing import Any

from aioboto3 import Session
from botocore.config import Config as BotocoreConfig
from botocore.exceptions import ClientError

from app.core.settings import Config as AppConfig
from app.core.settings import settings

from .base import BaseClient, BaseContextManager


class S3Client(BaseClient):
    """Клиент для работы с Amazon S3"""

    def __init__(self, settings: AppConfig = settings) -> None:
        super().__init__()
        self.settings = settings
        self.session = None
        self.client = None

    async def connect(self) -> Any:
        """Создает клиент S3"""
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
        """Закрывает клиент S3"""
        if self.client:
            self.logger.debug("Закрытие клиента S3...")
            self.client = None
            self.logger.info("Клиент S3 закрыт")


class S3ContextManager(BaseContextManager):
    """Контекстный менеджер для S3"""

    def __init__(self) -> None:
        super().__init__()
        self.s3_client = S3Client()
        self.client = None
        self.client_context = None

    async def __aenter__(self):
        self.client_context = await self.s3_client.connect()
        
        self.client = await self.client_context.__aenter__()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client_context:
            await self.client_context.__aexit__(exc_type, exc_val, exc_tb)
        await self.s3_client.close()

    async def connect(self) -> Any:
        return await self.s3_client.connect()

    async def close(self) -> None:
        await self.s3_client.close()
