from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.workspaces.service import WorkspaceService


class WorkspaceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def workspace_service(self, db_session: AsyncSession) -> WorkspaceService:
        return WorkspaceService(db_session)
