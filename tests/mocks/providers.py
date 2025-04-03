from unittest.mock import AsyncMock, MagicMock
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.database import DatabaseClient
from app.services.v1.workspaces.service import WorkspaceService

class MockDatabaseProvider(Provider):
    """Мок-провайдер для базы данных."""

    @provide(scope=Scope.APP)
    def provide_database_client(self) -> DatabaseClient:
        """Предоставляет мок для клиента базы данных."""
        mock = AsyncMock(spec=DatabaseClient)
        mock.session.return_value.__aenter__.return_value = AsyncMock(spec=AsyncSession)
        return mock

    @provide(scope=Scope.REQUEST)
    async def provide_db_session(self, client: DatabaseClient) -> AsyncSession:
        """Предоставляет мок для сессии базы данных."""
        return AsyncMock(spec=AsyncSession)

    @provide(scope=Scope.REQUEST)
    async def provide_workspace_service(self, session: AsyncSession) -> WorkspaceService:
        """Предоставляет мок для сервиса рабочих пространств."""
        mock = MagicMock(spec=WorkspaceService)
        # Настраиваем методы мока
        mock.create_workspace.return_value = {
            "data": {
                "id": 1,
                "name": "Test Workspace",
                "description": "Test Description",
                "is_public": False,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "owner_id": 1,
                "owner": {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@example.com"
                },
                "role": "OWNER"
            },
            "message": "Рабочее пространство успешно создано"
        }
        return mock
