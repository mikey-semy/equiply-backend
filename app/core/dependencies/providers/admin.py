from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.admin.service import AdminInitService

class AdminProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def admin_init_service(self, db_session: AsyncSession) -> AdminInitService:
        return AdminInitService(db_session)