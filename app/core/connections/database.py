"""
Модуль для работы с базой данных.

Предоставляет классы для управления подключением к PostgreSQL через SQLAlchemy:
- DatabaseClient: Клиент для установки и управления подключением к базе данных
- DatabaseContextManager: Контекстный менеджер для автоматического управления сессиями БД
- AsyncSessionFactory: Фабрика для создания асинхронных сессий

Модуль использует настройки подключения из конфигурации приложения и реализует
базовые интерфейсы из модуля base.py.
"""
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from app.core.settings import Config, settings

from .base import BaseClient, BaseContextManager


class DatabaseClient(BaseClient):
    """
    Клиент для работы с базой данных

    Реализует базовый класс BaseClient для установки и управления
    подключением к PostgreSQL через SQLAlchemy.

    Attributes:
        _settings (Config): Конфигурация с параметрами подключения к БД
        _engine (Optional[AsyncEngine]): Асинхронный движок SQLAlchemy
        _session_factory (Optional[async_sessionmaker]): Фабрика сессий
        logger (logging.Logger): Логгер для записи событий
    """

    def __init__(self, _settings: Config = settings) -> None:
        """
        Инициализирует клиент базы данных.

        Args:
            _settings (Config, optional): Конфигурация приложения.
                По умолчанию используется глобальная конфигурация.
        """
        super().__init__()
        self._settings = _settings
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None

    async def connect(self) -> async_sessionmaker:
        """
        Создает подключение к базе данных

        Устанавливает соединение с PostgreSQL и создает движок SQLAlchemy
        с фабрикой сессий.

        Returns:
            AsyncEngine: Асинхронный движок SQLAlchemy

        Raises:
            SQLAlchemyError: При ошибке подключения к базе данных

        Usage:
            ```python
            db_client = DatabaseClient()
            session_factory = await db_client.connect()
            async with session_factory() as session:
                # Работа с сессией
                result = await session.execute(query)
            ```
        """
        self.logger.debug("Подключение к базе данных...")
        self._engine = create_async_engine(
            url=self._settings.database_url,
            **self._settings.engine_params
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            **self._settings.session_params
        )
        self.logger.info("Подключение к базе данных установлено")
        return self._session_factory

    async def close(self) -> None:
        """
        Закрывает подключение к базе данных.

        Безопасно закрывает все соединения в пуле и освобождает ресурсы движка.

        Usage:
            ```python
            db_client = DatabaseClient()
            try:
                session_factory = await db_client.connect()
                # Работа с базой данных
            finally:
                await db_client.close()
            ```
        """
        if self._engine:
            self.logger.debug("Закрытие подключения к базе данных...")
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self.logger.info("Подключение к базе данных закрыто")


class DatabaseContextManager(BaseContextManager):
    """
    Контекстный менеджер для сессий базы данных.

    Упрощает работу с сессиями SQLAlchemy, автоматически управляя
    жизненным циклом сессии и подключения к базе данных.

    Attributes:
        db_client (DatabaseClient): Клиент базы данных для управления подключением.
        session (AsyncSession | None): Текущая активная сессия SQLAlchemy.
        logger (logging.Logger): Логгер для записи событий
    """

    def __init__(self) -> None:
        """
        Инициализирует контекстный менеджер базы данных.

        Создает экземпляр DatabaseClient для управления подключением.
        """
        super().__init__()
        self.db_client = DatabaseClient()
        self.session: AsyncSession | None = None

    async def connect(self) -> AsyncSession:
        """
        Устанавливает подключение к базе данных и создает сессию.

        Returns:
            AsyncSession: Асинхронная сессия SQLAlchemy для работы с базой данных.

        Usage:
            ```python
            db_manager = DatabaseContextManager()
            session = await db_manager.connect()

            # Работа с сессией
            result = await session.execute(query)

            # Фиксация изменений
            await db_manager.commit()

            # Закрытие сессии
            await db_manager.close()
            ```
        """
        session_factory = await self.db_client.connect()
        self.session = session_factory()
        return self.session

    async def close(self, do_rollback: bool = False) -> None:
        """
        Закрывает сессию и подключение к базе данных.

        Args:
            do_rollback (bool, optional): Флаг, указывающий, нужно ли выполнить
                откат транзакции перед закрытием сессии. По умолчанию False.

        Note:
            Если do_rollback=True, все незафиксированные изменения будут отменены.
            Если do_rollback=False, незафиксированные изменения останутся в сессии,
            но не будут применены к базе данных.

        Usage:
            ```python
            # Закрытие сессии без отката транзакции
            await db_manager.close()

            # Закрытие сессии с откатом транзакции
            await db_manager.close(do_rollback=True)
            ```
        """
        if self.session:
            if do_rollback:
                await self.session.rollback()
            await self.session.close()
            self.session = None
        await self.db_client.close()

    async def commit(self) -> None:
        """
        Фиксирует изменения в базе данных.

        Применяет все изменения, сделанные в текущей транзакции.

        Raises:
            RuntimeError: Если сессия не была инициализирована.

        Usage:
            ```python
            # Создание новой записи
            new_user = User(username="john_doe")
            session.add(new_user)

            # Фиксация изменений
            await db_manager.commit()
            ```
        """
        if self.session:
            await self.session.commit()
