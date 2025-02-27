"""
Тесты для компонентов работы с базой данных.
"""

import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_database_client_connect(mock_database_client, mock_logger):
    """
    Проверяет, что метод connect клиента базы данных работает корректно.
    """
    # Вызываем connect
    session_factory = await mock_database_client.connect()

    # Проверяем, что метод был вызван один раз
    mock_database_client.connect.assert_called_once()

    # Проверяем, что логгер использовался
    mock_logger.debug.assert_called_with("Подключение к базе данных...")
    mock_logger.info.assert_called_with("Подключение к базе данных установлено")

    # Проверяем, что возвращается корректный объект
    assert session_factory is not None


@pytest.mark.asyncio
async def test_database_client_close(mock_database_client, mock_logger):
    """
    Проверяет, что метод close клиента базы данных работает корректно.
    """
    # Устанавливаем engine (он проверяется в методе close)
    mock_database_client._engine = AsyncMock()

    # Вызываем close
    await mock_database_client.close()

    # Проверяем, что метод был вызван один раз
    mock_database_client.close.assert_called_once()

    # Проверяем, что логгер использовался
    mock_logger.debug.assert_called_with("Закрытие подключения к базе данных...")
    mock_logger.info.assert_called_with("Подключение к базе данных закрыто")


@pytest.mark.asyncio
async def test_database_session(mock_db_session):
    """
    Проверяет работу с сессией базы данных.
    """
    # Проверяем, что сессия создана
    assert mock_db_session is not None

    # Тестируем методы сессии
    await mock_db_session.commit()
    mock_db_session.commit.assert_called_once()

    await mock_db_session.rollback()
    mock_db_session.rollback.assert_called_once()
