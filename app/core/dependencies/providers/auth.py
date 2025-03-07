from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.services.v1.auth import AuthService
from app.core.settings import settings

class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def auth_service(self, db_session: AsyncSession) -> AuthService:
        return AuthService(db_session)
    
    @provide(scope=Scope.APP)
    def oauth2_schema(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(
            tokenUrl=settings.AUTH_URL, 
            auto_error=True, 
            scheme_name="OAuth2PasswordBearer"
        )
