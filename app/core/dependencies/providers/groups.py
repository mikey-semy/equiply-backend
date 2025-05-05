from dishka import Provider, Scope, provide

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.groups.service import GroupService


class GroupProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_service(self, db_session: AsyncSession) -> GroupService:
        return GroupService(db_session)
