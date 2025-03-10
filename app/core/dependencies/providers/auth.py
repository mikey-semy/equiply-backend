from dishka import Provider, provide, Scope
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.auth.service import AuthService

class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def auth_service(self, db_session: AsyncSession, redis: Redis) -> AuthService:
        return AuthService(db_session, redis)
