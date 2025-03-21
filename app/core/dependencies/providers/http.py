from typing import AsyncGenerator

from dishka import Provider, Scope, provide

from app.core.connections.http import HttpClient


class HttpProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_client(self) -> AsyncGenerator[HttpClient, None]:
        client = HttpClient()
        await client.connect()
        yield client
        await client.close()
