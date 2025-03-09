from dishka import Provider, provide, Scope
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer

from app.services.v1.auth.service import AuthService
from app.core.settings import settings
from app.core.connections.auth import get_current_user
from app.schemas import UserCredentialsSchema


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def auth_service(self, db_session: AsyncSession, redis: Redis) -> AuthService:
        return AuthService(db_session, redis)

    @provide(scope=Scope.APP)
    def oauth2_schema(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(
            tokenUrl=settings.AUTH_URL,
            auto_error=True,
            scheme_name="OAuth2PasswordBearer"
        )

    @provide(scope=Scope.REQUEST)
    async def current_user(self) -> UserCredentialsSchema:
        return await get_current_user