"""
Модуль для работы с базой данных и сессиями SQLAlchemy.

Этот модуль предоставляет классы и функции для инициализации подключения к базе данных,
создания асинхронных сессий и управления ими с использованием SQLAlchemy.

Основные компоненты:
- DatabaseClient: Класс для настройки подключения к базе данных и создания фабрики сессий.
- SessionContextManager: Контекстный менеджер для управления жизненным циклом сессий.

Модуль использует асинхронные возможности SQLAlchemy для эффективной работы с базой данных
в асинхронных приложениях.
"""

from typing import Any

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from app.core.settings import settings


class DatabaseClient:
    """
    Класс для инициализации и настройки подключения к базе данных и компонентов ORM.
    """

    def __init__(self, _settings: Any = settings) -> None:
        """
        Инициализирует экземпляр DatabaseClient.

        Args:
            _settings (Any): Объект конфигурации.
        """
        self._settings = _settings
        self.dsn = _settings.database_dsn

    def __get_dsn(self, dsn: str) -> str:
        """
        Получает dsn.

        Args:
            dsn (str): url dsn.

        Returns:
            str: url dsn.
        """
        return dsn

    def __create_async_engine(self, dsn: str) -> AsyncEngine:
        """
        Создает асинхронный движок SQLAlchemy.

        Args:
            dsn (str): Строка подключения к базе данных.
            engine_params (Dict[str, bool]): Параметры для создания движка.

        Returns:
            AsyncEngine: Асинхронный движок SQLAlchemy.
        """
        async_engine = create_async_engine(dsn, **self._settings.database_params)

        return async_engine

    def __precreate_async_session_factory(
        self, async_engine: AsyncEngine
    ) -> AsyncSession:
        """
        Предварительно создает фабрику асинхронных сессий для операций с базой данных.

        Args:
            async_engine (AsyncEngine): Асинхронный движок SQLAlchemy.
            sessionmaker_params (Dict[str, Any]): Параметры для создания сессии.

        Returns:
            AsyncSession: Фабрика асинхронных сессий.
        """
        async_session_factory = async_sessionmaker(
            bind=async_engine,
            **self._settings.database_params
        )
        return async_session_factory

    def create_async_session_factory(self) -> AsyncSession:
        """
        Создает настроенную фабрику сессий.

        Returns:
            AsyncSession: Фабрика асинхронных сессий.
        """

        dsn = self.__get_dsn(self.dsn)

        async_engine = self.__create_async_engine(dsn)

        session_factory = self.__precreate_async_session_factory(async_engine)

        return session_factory


class SessionContextManager:
    """
    Контекстный менеджер для управления сессиями базы данных.
    """

    def __init__(self) -> None:
        """
        Инициализирует экземпляр SessionContextManager.
        """
        self.db_session = DatabaseClient()
        self.session_factory = self.db_session.create_async_session_factory()
        self.session = None

    async def __aenter__(self) -> "SessionContextManager":
        """
        Асинхронный метод входа в контекстный менеджер.

        Returns:
            SessionContextManager: Экземпляр текущего контекстного менеджера.
        """
        self.session = self.session_factory()
        return self

    async def __aexit__(self, *args: object) -> None:
        """
        Асинхронный метод выхода из контекстного менеджера.

        Args:
            *args: Аргументы, передаваемые при выходе из контекста.
        """
        await self.rollback()

    async def commit(self) -> None:
        """
        Асинхронно фиксирует изменения в базе данных и закрывает сессию.
        """
        await self.session.commit()
        await self.session.close()
        self.session = None

    async def rollback(self) -> None:
        """
        Асинхронно откатывает изменения в базе данных и закрывает сессию.
        """
        await self.session.rollback()
        await self.session.close()
        self.session = None
