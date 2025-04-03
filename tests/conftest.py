import pytest

from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.routes.v1.workspaces import get_current_user
from app.services.v1.workspaces.service import WorkspaceService


# Мокаем RabbitMQ и другие внешние зависимости
@pytest.fixture(autouse=True)
def mock_external_dependencies():
    """Мокает внешние зависимости, такие как RabbitMQ и Redis."""
    with patch("app.core.connections.messaging.RabbitMQClient.connect", new_callable=AsyncMock) as mock_connect, \
         patch("app.core.connections.messaging.RabbitMQClient.close", new_callable=AsyncMock) as mock_close, \
         patch("faststream.broker.core.usecase.BrokerUsecase.start", new_callable=AsyncMock) as mock_start, \
         patch("faststream.broker.core.usecase.BrokerUsecase.connect", new_callable=AsyncMock) as mock_broker_connect:
        yield {
            "rabbit_connect": mock_connect,
            "rabbit_close": mock_close,
            "broker_start": mock_start,
            "broker_connect": mock_broker_connect
        }

@pytest.fixture
def mock_current_user():
    """Возвращает мок текущего пользователя."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

@pytest.fixture
def workspace_service_mock():
    """Создает мок для сервиса рабочих пространств."""
    mock = MagicMock(spec=WorkspaceService)
    mock.create_workspace = AsyncMock()
    return mock

@pytest.fixture
def client():
    """Создает тестовый клиент."""
    # Переопределяем зависимость для получения текущего пользователя
    async def mock_get_current_user():
        return {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }

    app.dependency_overrides[get_current_user] = mock_get_current_user

    with TestClient(app) as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()
