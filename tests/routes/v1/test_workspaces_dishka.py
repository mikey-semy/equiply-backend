import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.workspaces.service import WorkspaceService
from app.schemas import CurrentUserSchema, CreateWorkspaceSchema
from app.models.v1.workspaces import WorkspaceModel, WorkspaceMemberModel

@pytest.fixture
def mock_current_user():
    """Мок для текущего пользователя."""
    return CurrentUserSchema(
        id=1,
        username="testuser",
        email="test@example.com",
        role="user",
        is_active=True,
        is_verified=True
    )

@pytest.fixture
def mock_db_session():
    """Создает мок для сессии базы данных."""
    session = AsyncMock(spec=AsyncSession)

    # Настраиваем execute для имитации запросов
    execute_mock = AsyncMock()
    session.execute.return_value = execute_mock

    # Настраиваем scalar_one_or_none для имитации результатов запросов
    execute_mock.scalar_one_or_none.side_effect = [
        None,  # Первый вызов - проверка существования (не существует)
        MagicMock(  # Второй вызов - получение созданного объекта
            id=1,
            name="Test Workspace",
            description="Test Description",
            is_public=False,
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
            owner_id=1,
            owner=MagicMock(
                id=1,
                username="testuser",
                email="test@example.com"
            )
        )
    ]

    return session

@pytest.mark.asyncio
async def test_create_workspace_real(mock_db_session, mock_current_user):
    """Тестирует создание рабочего пространства с реальным сервисом."""
    # Создаем реальный сервис с моком для базы данных
    service = WorkspaceService(db_session=mock_db_session)

    # Подготовка данных
    workspace_data = CreateWorkspaceSchema(
        name="Test Workspace",
        description="Test Description",
        is_public=False
    )

    # Вызываем метод сервиса
    result = await service.create_workspace(workspace_data, mock_current_user)

    # Проверка результатов
    assert result["data"]["id"] == 1
    assert result["data"]["name"] == workspace_data.name
    assert result["message"] == "Рабочее пространство успешно создано"

    # Проверяем, что сервис правильно взаимодействовал с базой данных
    assert mock_db_session.execute.call_count >= 2  # Минимум 2 запроса
    assert mock_db_session.commit.called  # Был вызван commit

    # Проверяем, что был вызван add для создания объектов
    # Это требует более сложной настройки мока, но можно сделать так:
    mock_db_session.add.assert_any_call(pytest.raises(Exception, match="WorkspaceModel"))
    mock_db_session.add.assert_any_call(pytest.raises(Exception, match="WorkspaceMemberModel"))
