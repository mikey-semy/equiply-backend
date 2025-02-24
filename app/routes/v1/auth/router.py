from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, oauth2_schema
from app.routes.base import BaseRouter
from app.schemas import AuthSchema, TokenResponseSchema
from app.services import AuthService

class AuthRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="auth", tags=["Authentication"])

    def configure(self):
        @self.router.post("")
        async def authenticate(
            form_data: OAuth2PasswordRequestForm = Depends(),
            db_session: AsyncSession = Depends(get_db_session),
        ) -> TokenResponseSchema:
            """🔐 Аутентифицирует пользователя"""
            return await AuthService(db_session).authenticate(
                AuthSchema(email=form_data.username, password=form_data.password)
            )

        @self.router.post("/logout")
        async def logout(
            token: str = Depends(oauth2_schema),
            db_session: AsyncSession = Depends(get_db_session),
        ) -> dict:
            """👋 Выход из системы"""
            return await AuthService(db_session).logout(token)
