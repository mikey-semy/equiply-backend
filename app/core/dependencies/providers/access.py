# from dishka import Provider, Scope, provide
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.services.v1.access.service import AccessControlService


# class AccessProvider(Provider):
#     @provide(scope=Scope.REQUEST)
#     def access_service(self, db_session: AsyncSession) -> AccessControlService:
#         return AccessControlService(db_session)
