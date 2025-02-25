from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.dependencies import get_db_session
from app.routes.base import BaseRouter
# from app.schemas import RegistrationResponseSchema, RegistrationSchema, VerificationResponseSchema
# from app.services import UserService

class RegisterRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="register", tags=["Registration"])

    def configure(self):
        pass
        # @self.router.post("/")
        # async def registration_user(
        #     user: RegistrationSchema,
        #     db_session: AsyncSession = Depends(get_db_session),
        # ) -> RegistrationResponseSchema:
        #     """📝 Регистрирует нового пользователя"""
        #     return await UserService(db_session).create_user(user)

        # @self.router.get("/verify-email/{token}")
        # async def verify_email(
        #     token: str,
        #     db_session: AsyncSession = Depends(get_db_session)
        # ) -> VerificationResponseSchema:
        #     """✉️ Подтверждение email адреса"""
        #     return await UserService(db_session).verify_email(token)
