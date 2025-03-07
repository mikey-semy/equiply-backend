from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from dishka.integrations.fastapi import FromDishka, inject

from app.routes.base import BaseRouter
from app.schemas import TokenResponseSchema
from app.services.v1.auth.service import AuthService

class AuthRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="auth", tags=["Authentication"])

    def configure(self):
        @self.router.post("/", response_model=TokenResponseSchema)
        @inject
        async def authenticate(
            auth_service: FromDishka[AuthService],
            form_data: OAuth2PasswordRequestForm = Depends()
        ) -> TokenResponseSchema:
            """
            🔐 Аутентифицирует пользователя по имени, email или телефону

            Для аутентификации используйте:
            - Email-адрес
            - Имя пользователя
            - Телефон в формате +7 (XXX) XXX-XX-XX
            """
            return await auth_service.authenticate(form_data)

        @self.router.post("/logout")
        @inject
        async def logout(
            token: str,
            auth_service: FromDishka[AuthService]
        ) -> dict:
            """👋 Выход из системы"""
            return await auth_service.logout(token)
