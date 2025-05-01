from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.access.service import AccessControlService
from app.services.v1.access.base import PolicyService

class AccessProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def access_service(self, db_session: AsyncSession) -> AccessControlService:
        return AccessControlService(db_session)

    @provide(scope=Scope.REQUEST)
    def policy_service(self, db_session: AsyncSession, access_service: AccessControlService) -> PolicyService:
        return PolicyService(db_session, access_service)