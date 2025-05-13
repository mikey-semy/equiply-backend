from botocore.client import BaseClient
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.integrations.storage.avatars import AvatarS3DataManager
from app.services.v1.modules.tables.service import TableService


class TableProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def table_service(
        self, db_session: AsyncSession, s3_client: BaseClient
    ) -> TableService:
        return TableService(
            db_session, s3_data_manager=AvatarS3DataManager(s3_client)
        )
