from typing import Any
from aiologger import Logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from app.core.settings import settings
from .base import BaseClient, BaseContextManager

class DatabaseClient(BaseClient):
    """Клиент для работы с базой данных"""

    def __init__(self, logger: Logger, _settings: Any = settings) -> None:
        super().__init__(logger)
        self._settings = _settings
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None

    def _create_engine(self) -> AsyncEngine:
        """Создает движок SQLAlchemy"""
        return create_async_engine(
            self._settings.database_dsn,
            **self._settings.database_params
        )

    def _create_session_factory(self) -> async_sessionmaker:
        """Создает фабрику сессий"""
        return async_sessionmaker(
            bind=self._engine,
            **self._settings.database_params
        )

    async def connect(self) -> async_sessionmaker:
        """Инициализирует подключение к БД"""
        await self._logger.debug("Подключение к базе данных...")
        self._engine = self._create_engine()
        self._session_factory = self._create_session_factory()
        await self._logger.info("Подключение к базе данных установлено")
        return self._session_factory

    async def close(self) -> None:
        """Закрывает подключение к БД"""
        if self._engine:
            await self._logger.debug("Закрытие подключения к базе данных...")
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            await self._logger.info("Подключение к базе данных закрыто")

class DatabaseContextManager(BaseContextManager):
    """Контекстный менеджер для сессий БД"""

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)
        self.db_client = DatabaseClient(logger)
        self.session: AsyncSession | None = None

    async def connect(self) -> AsyncSession:
        session_factory = await self.db_client.connect()
        self.session = session_factory()
        return self.session

    async def close(self) -> None:
        if self.session:
            await self.session.rollback()
            await self.session.close()
            self.session = None
        await self.db_client.close()

    async def commit(self) -> None:
        """Фиксирует изменения в БД"""
        if self.session:
            await self.session.commit()
