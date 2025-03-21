from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.register.service import RegisterService


class RegisterProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def register_service(self, db_session: AsyncSession) -> RegisterService:
        return RegisterService(db_session)
