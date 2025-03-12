from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession
from aioboto3 import Session
from app.services.v1.avatar.service import AvatarService

class AvatarProvider(Provider):
    @provide(scope=Scope.REQUEST) 
    def avatar_service(self, db_session: AsyncSession, s3: Session) -> AvatarService:
        return AvatarService(db_session, s3)