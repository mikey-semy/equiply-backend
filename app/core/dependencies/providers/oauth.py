from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.oauth.service import OAuthService

class OAuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def oauth_service(self, db_session: AsyncSession) -> OAuthService:
        return OAuthService(db_session)
