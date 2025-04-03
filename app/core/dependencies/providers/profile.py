from botocore.client import BaseClient
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.integrations.storage.avatars import AvatarS3DataManager
from app.services.v1.profile.service import ProfileService


class ProfileProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def profile_service(
        self, db_session: AsyncSession, s3_client: BaseClient
    ) -> ProfileService:
        return ProfileService(
            db_session, s3_data_manager=AvatarS3DataManager(s3_client)
        )
