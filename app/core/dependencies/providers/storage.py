from typing import AsyncGenerator
from aiologger import Logger
from botocore.client import BaseClient
from dishka import Provider, provide, Scope
from dishka.integrations.fastapi import FromDishka
from app.core.dependencies.connections.storage import S3ContextManager

class S3Provider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_client(self, logger: FromDishka[Logger]) -> AsyncGenerator[BaseClient, None]:
        async with S3ContextManager(logger) as client:
            yield client
