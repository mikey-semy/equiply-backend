from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

from app.services.v1.oauth.service import OAuthService
from app.services.v1.auth.service import AuthService
from app.services.v1.users.service import UserService
from app.core.integrations.cache.oauth import OAuthRedisStorage

class OAuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def oauth_service(
        self,
        db_session: AsyncSession,
        auth_service: AuthService,
        user_service: UserService,
        redis: Redis,
    ) -> OAuthService:
        service = OAuthService(db_session)
        service.auth_service = auth_service
        service.user_service = user_service
        service.redis_storage = OAuthRedisStorage(redis)
        return service
