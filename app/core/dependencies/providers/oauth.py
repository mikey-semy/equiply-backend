from dishka import Provider, Scope, provide
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.integrations.cache.oauth import OAuthRedisStorage
from app.services.v1.auth.service import AuthService
from app.services.v1.oauth.service import OAuthService
from app.services.v1.register.service import RegisterService


class OAuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def oauth_service(
        self,
        db_session: AsyncSession,
        auth_service: AuthService,
        register_service: RegisterService,
        redis: Redis,
    ) -> OAuthService:
        return OAuthService(
            db_session,
            auth_service=auth_service,
            register_service=register_service,
            redis_storage=OAuthRedisStorage(redis),
        )
