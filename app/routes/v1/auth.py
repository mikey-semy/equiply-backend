from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from dishka.integrations.fastapi import FromDishka, inject

from app.routes.base import BaseRouter
from app.schemas import TokenResponseSchema, ForgotPasswordSchema, PasswordResetResponseSchema, PasswordResetConfirmSchema, PasswordResetConfirmResponseSchema
from app.services.v1.auth.service import AuthService

class AuthRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="auth", tags=["Authentication"])

    def configure(self):
        @self.router.post("", response_model=TokenResponseSchema)
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

        @self.router.post("/forgot-password", response_model=PasswordResetResponseSchema)
        @inject
        async def forgot_password(
            email_data: ForgotPasswordSchema,
            auth_service: FromDishka[AuthService]
        ) -> PasswordResetResponseSchema:
            """📧 Отправка ссылки для восстановления пароля на email"""
            return await auth_service.send_password_reset_email(email_data.email)

        @self.router.post("/reset-password/{token}", response_model=PasswordResetConfirmResponseSchema)
        @inject
        async def reset_password(
            token: str,
            password_data: PasswordResetConfirmSchema,
            auth_service: FromDishka[AuthService]
        ) -> PasswordResetConfirmResponseSchema:
            """🔄 Установка нового пароля по токену сброса"""
            return await auth_service.reset_password(token, password_data.password)