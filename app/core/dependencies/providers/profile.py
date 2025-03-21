from dishka import Provider, Scope, provide
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.profile.service import ProfileService


class ProfileProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def profile_service(self, db_session: AsyncSession, redis: Redis) -> ProfileService:
        return ProfileService(db_session, redis)
