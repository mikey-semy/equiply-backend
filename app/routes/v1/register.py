from dishka.integrations.fastapi import FromDishka, inject
from app.routes.base import BaseRouter
from app.schemas import RegistrationResponseSchema, RegistrationSchema, VerificationResponseSchema
from app.services.v1.register.service import RegisterService

class RegisterRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="register", tags=["Registration"])

    def configure(self):
        @self.router.post("")
        @inject
        async def registration_user(
            new_user: RegistrationSchema,
            register_service: FromDishka[RegisterService]
        ) -> RegistrationResponseSchema:
            """📝 Регистрирует нового пользователя"""
            return await register_service.create_user(new_user)

        @self.router.get("/verify-email/{token}")
        @inject
        async def verify_email(
            token: str,
            register_service: FromDishka[RegisterService]
        ) -> VerificationResponseSchema:
            """✉️ Подтверждение email адреса"""
            return await register_service.verify_email(token)
