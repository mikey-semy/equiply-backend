from fastapi.security import OAuth2PasswordRequestForm
from dishka.integrations.fastapi import FromDishka, inject

from app.routes.base import BaseRouter
from app.schemas import AuthSchema, TokenResponseSchema
from app.services.v1.auth.service import AuthService

class AuthRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="auth", tags=["Authentication"])

    def configure(self):
        @self.router.post("")
        @inject
        async def authenticate(
            form_data: OAuth2PasswordRequestForm,
            auth_service: FromDishka[AuthService]
        ) -> TokenResponseSchema:
            """🔐 Аутентифицирует пользователя"""
            return await auth_service.authenticate(
                AuthSchema(email=form_data.username, password=form_data.password)
            )

        @self.router.post("/logout")
        @inject
        async def logout(
            token: str,
            auth_service: FromDishka[AuthService]
        ) -> dict:
            """👋 Выход из системы"""
            return await auth_service.logout(token)
