"""
Модуль содержит мок-провайдеры для тестирования компонентов приложения.

В этом модуле определены провайдеры, которые заменяют реальные провайдеры
приложения на моки для изолированного тестирования. Эти провайдеры можно
использовать с dishka-контейнером в тестах для внедрения зависимостей.

Преимущества использования мок-провайдеров:
1. Изоляция тестируемых компонентов от внешних зависимостей
2. Ускорение выполнения тестов (не требуются реальные соединения с БД)
3. Возможность проверить вызовы методов логгирования, SQL-запросов и т.д.
4. Избегание побочных эффектов при тестировании

Примеры использования находятся в файлах тестов, например tests/test_database.py
"""

from unittest.mock import AsyncMock
from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.connections.database import DatabaseClient


class MockDatabaseProvider(Provider):
    """
    Мок-провайдер для тестирования компонентов, зависящих от базы данных.

    Этот провайдер создает моки для DatabaseClient и AsyncSession,
    которые можно использовать в тестах вместо реальных объектов.
    Все методы моков можно отслеживать и проверять их вызовы в тестах.

    Attributes:
        Наследует атрибуты базового класса Provider из dishka.

    Examples:
        ```python
        # Создание тестового контейнера с мок-провайдером
        container = make_container(MockDatabaseProvider())
        # Получение мок-клиента из контейнера
        db_client = await container.get(DatabaseClient)
        # Проверка вызова метода
        db_client.connect.assert_called_once()
        ```
    """

    @provide(scope=Scope.APP)
    def get_database_client(self) -> DatabaseClient:
        """
        Создает и возвращает мок DatabaseClient.

        Этот метод создает AsyncMock с интерфейсом DatabaseClient,
        который можно использовать для проверки вызовов методов в тестах.

        Returns:
            AsyncMock объект, имитирующий DatabaseClient
        """
        client = AsyncMock(spec=DatabaseClient)
        # Настраиваем поведение мока
        client.connect = AsyncMock(
            return_value=AsyncMock(spec=async_sessionmaker)
        )
        client.close = AsyncMock()
        # Важно: DatabaseClient возвращает session_factory из connect()
        return client

    @provide(scope=Scope.REQUEST)
    async def get_session(self, database_client: DatabaseClient) -> AsyncSession:
        """
        Создает и возвращает мок AsyncSession для тестирования.

        Этот метод имитирует контекстный менеджер сессии, который обычно
        используется в приложении, но без реального подключения к БД.

        Args:
            database_client: Мок клиента базы данных (внедряется контейнером)

        Yields:
            AsyncMock объект, имитирующий AsyncSession
        """
        session = AsyncMock(spec=AsyncSession)
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        # Функция-генератор для имитации контекстного менеджера
        yield session
