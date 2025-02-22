from typing import AsyncGenerator
from aiologger import Logger
from botocore.client import BaseClient
from dishka import Provider, provide, Scope
from dishka.integrations.fastapi import FromDishka
from app.core.dependencies.contexts.s3 import SessionContextManager

class S3Provider(Provider):
    """
    Провайдер для управления клиентом S3.

    Предоставляет доступ к S3 клиенту в рамках запроса.
    Использует контекстный менеджер для управления подключением.

    Attributes:
        client (BaseClient): Клиент S3.

    Methods:
        get_client: Возвращает клиент S3.
    """
    @provide(scope=Scope.REQUEST)
    async def get_client(self, logger: FromDishka[Logger]) -> AsyncGenerator[BaseClient, None]:
        """
        Возвращает клиент S3.

        Returns:
            BaseClient: Клиент S3.
        """
        async with SessionContextManager(logger=logger) as client:
            yield client
