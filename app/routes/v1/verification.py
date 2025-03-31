from dishka.integrations.fastapi import FromDishka, inject

from app.routes.base import BaseRouter
from app.schemas import (
    ResendVerificationRequestSchema,
    ResendVerificationResponseSchema,
    VerificationStatusResponseSchema
)
from app.schemas.v1.users.exceptions import UserNotFoundResponseSchema
from app.services.v1.register.service import RegisterService


class VerificationRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="verification", tags=["Verification"])

    def configure(self):
        @self.router.post(
            path="/resend",
            response_model=ResendVerificationResponseSchema,
            responses={
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден",
                },
            },
        )
        @inject
        async def resend_verification_email(
            request: ResendVerificationRequestSchema,
            register_service: FromDishka[RegisterService]
        ) -> ResendVerificationResponseSchema:
            """
            ## 📧 Повторная отправка письма для подтверждения email

            Отправляет новое письмо для подтверждения email адреса зарегистрированного пользователя

            ### Args:
            * **email**: Email пользователя

            ### Returns:
            * Статус отправки письма
            """
            await register_service.resend_verification_email(request.email)
            return ResendVerificationResponseSchema(email=request.email)

        @self.router.get(
            path="/status/{email}",
            response_model=VerificationStatusResponseSchema,
            responses={
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден",
                },
            },
        )
        @inject
        async def check_verification_status(
            email: str, register_service: FromDishka[RegisterService]
        ) -> VerificationStatusResponseSchema:
            """
            ## ✅ Проверка статуса верификации

            Проверяет, подтвержден ли email адрес пользователя

            ### Args:
            * **email**: Email пользователя

            ### Returns:
            * Статус верификации email
            """
            is_verified = await register_service.check_verification_status(email)
            return VerificationStatusResponseSchema(
                email=email,
                is_verified=is_verified
            )
