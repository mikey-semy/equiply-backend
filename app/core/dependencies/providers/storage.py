from typing import AsyncGenerator
from botocore.client import BaseClient
from dishka import Provider, provide, Scope
from app.core.connections.storage import S3ContextManager

class S3Provider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_client(self) -> AsyncGenerator[BaseClient, None]:
        async with S3ContextManager() as client:
            yield client
