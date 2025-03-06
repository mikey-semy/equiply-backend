import logging
from typing import Any, Optional
from abc import ABC, abstractmethod

class BaseClient(ABC):
    """Базовый класс для всех клиентов"""

    def __init__(self) -> None:
        self._client: Optional[Any] = None
        self.logger = logging.getLogger(self.__class__.__name__)

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

    def __init__(self) -> None:
        self._client = None

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
