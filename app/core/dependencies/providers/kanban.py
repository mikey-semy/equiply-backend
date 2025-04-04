from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.modules.kanban.service import KanbanService


class KanbanProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def kanban_service(self, db_session: AsyncSession) -> KanbanService:
        return KanbanService(db_session)
