from typing import AsyncGenerator
from aiologger import Logger
from dishka import Provider, provide, Scope
from dishka.integrations.fastapi import FromDishka
from app.core.dependencies.connections.http import HttpClient

class HttpProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_client(self, logger: FromDishka[Logger]) -> AsyncGenerator[HttpClient, None]:
        client = HttpClient(logger)
        await client.connect()
        yield client
        await client.close()
