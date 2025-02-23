from dishka import Provider, provide, Scope
from aiologger import Logger
from app.core.lifespan.state import AppState

class LoggerProvider(Provider):
    """
    Провайдер для логгера приложения.

    Attributes:
        logger (Logger): Логгер приложения.

    Methods:
        get_client: Возвращает логгер приложения.
    """
    @provide(scope=Scope.APP)
    async def get_client(self) -> Logger:
        """
        Возвращает логгер приложения.

        Returns:
            Logger: Логгер приложения.
        """
        return AppState.logger