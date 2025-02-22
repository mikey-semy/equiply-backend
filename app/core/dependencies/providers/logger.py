from dishka import Provider, provide, Scope
from aiologger import Logger
from app.core.lifespan.state import AppState

class LoggerProvider(Provider):
    """
    Провайдер для логгера приложения.
    """
    @provide(scope=Scope.APP)
    async def get_logger(self) -> Logger:
        return AppState.logger