from dishka import Provider, provide, Scope
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.workspaces.service import WorkspaceService

class WorkspaceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def workspace_service(self, db_session: AsyncSession, redis: Redis) -> WorkspaceService:
        return WorkspaceService(db_session, redis)
