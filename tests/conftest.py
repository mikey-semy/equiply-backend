import os
import sys
from pathlib import Path
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from aiologger import Logger
from dishka import make_container, Scope, Provider, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies.connections.database import DatabaseClient
from tests.mocks.providers import MockDatabaseProvider


# Провайдер для мок-логгера
class MockLoggerProvider(Provider):
    @provide(scope=Scope.APP)
    def get_logger(self) -> Logger:
        logger = AsyncMock(spec=Logger)
        logger.debug = AsyncMock()
        logger.info = AsyncMock()
        logger.warning = AsyncMock()
        logger.error = AsyncMock()
        return logger


@pytest_asyncio.fixture
async def test_container():
    """Создает тестовый контейнер с мок-провайдерами."""
    container = make_container(
        MockLoggerProvider(),
        MockDatabaseProvider(),
    )
    yield container
    await container.close()


@pytest_asyncio.fixture
async def mock_logger(test_container):
    """Возвращает мок-логгер из контейнера."""
    return await test_container.get(Logger)


@pytest_asyncio.fixture
async def mock_database_client(test_container):
    """Возвращает мок клиента базы данных."""
    return await test_container.get(DatabaseClient)


@pytest_asyncio.fixture
async def mock_db_session(test_container):
    """Возвращает мок-сессию базы данных."""
    async with test_container.enter_scope(Scope.REQUEST):
        yield await test_container.get(AsyncSession)


def pytest_configure(config):
    """Установка переменной окружения для тестов"""
    root_dir = Path(__file__).parent.parent
    os.environ["ENV_FILE"] = str(root_dir / ".env.test")


# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
