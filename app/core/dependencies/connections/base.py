from typing import Any, Optional
from abc import ABC, abstractmethod
from aiologger import Logger

class BaseClient(ABC):
    """Базовый класс для всех клиентов"""

    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._client: Optional[Any] = None

    @abstractmethod
    async def connect(self) -> Any:
        """Создает подключение"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Закрывает подключение"""
        pass

class BaseContextManager(ABC):
    """Базовый контекстный менеджер"""

    def __init__(self, logger: Logger) -> None:
        self._client = None
        self._logger = logger

    @abstractmethod
    async def connect(self) -> Any:
        """Создает подключение"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Закрывает подключение"""
        pass

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
