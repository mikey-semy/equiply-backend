from dishka import Provider, provide, Scope
from aiologger import Logger
from app.core.dependencies.connections.logger import LoggerClient

class LoggerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_client(self) -> Logger:
        return await LoggerClient.get_instance()
