from dishka import Provider, provide, Scope
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.users.service import UserService

class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_service(self, db_session: AsyncSession, redis: Redis) -> UserService:
        return UserService(db_session, redis)