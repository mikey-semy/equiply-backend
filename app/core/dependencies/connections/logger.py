from typing import Optional
from aiologger import Logger
from app.core.logging import setup_logging

class LoggerClient:
    """Синглтон для логгера"""
    _instance: Optional[Logger] = None

    @classmethod
    async def get_instance(cls) -> Logger:
        if not cls._instance:
            cls._instance = await setup_logging()
        return cls._instance

    @classmethod
    async def shutdown(cls) -> None:
        if cls._instance:
            await cls._instance.shutdown()
            cls._instance = None
