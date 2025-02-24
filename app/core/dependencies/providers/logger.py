from dishka import Provider, provide, Scope
from aiologger import Logger
from app.core.logging import setup_logging

class LoggerProvider(Provider):
    
    """
    Провайдер для логгера приложения.

    Attributes:
        logger (Logger): Логгер приложения.

    Methods:
        get_client: Возвращает логгер приложения.
    """
    _logger: Logger | None = None

    @provide(scope=Scope.APP)
    async def get_client(self) -> Logger:
        """
        Возвращает логгер приложения.

        Returns:
            Logger: Логгер приложения.
        """
        if not self._logger:
            self._logger = await setup_logging()
        return self._logger