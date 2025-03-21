from dishka.integrations.fastapi import FromDishka, inject

from app.routes.base import BaseRouter
from app.schemas import (RegistrationResponseSchema, RegistrationSchema,
                         VerificationResponseSchema)
from app.schemas.v1.register.exceptions import (TokenExpiredResponseSchema,
                                                TokenInvalidResponseSchema,
                                                UserCreationResponseSchema,
                                                UserExistsResponseSchema)
from app.schemas.v1.users.exceptions import UserNotFoundResponseSchema
from app.services.v1.register.service import RegisterService


class RegisterRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="register", tags=["Registration"])

    def configure(self):
        @self.router.post(
            path="/",
            response_model=RegistrationResponseSchema,
            responses={
                409: {
                    "model": UserExistsResponseSchema,
                    "description": "Пользователь с таким email/username/телефоном уже существует",
                },
                500: {
                    "model": UserCreationResponseSchema,
                    "description": "Ошибка при создании пользователя",
                },
            },
        )
        @inject
        async def registration_user(
            new_user: RegistrationSchema, register_service: FromDishka[RegisterService]
        ) -> RegistrationResponseSchema:
            """
            ## 📝 Регистрация нового пользователя

            Регистрирует нового пользователя в системе и отправляет письмо для подтверждения email

            ### Args:
            * **username**: Имя пользователя
            * **email**: Email пользователя
            * **password**: Пароль пользователя
            * **phone**: Телефон пользователя (опционально)

            ### Returns:
            * Информация о созданном пользователе и статус операции
            """
            return await register_service.create_user(new_user)

        @self.router.get(
            path="/verify-email/{token}",
            response_model=VerificationResponseSchema,
            responses={
                400: {
                    "model": TokenInvalidResponseSchema,
                    "description": "Недействительный токен верификации",
                },
                419: {
                    "model": TokenExpiredResponseSchema,
                    "description": "Срок действия токена истек",
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден",
                },
            },
        )
        @inject
        async def verify_email(
            token: str, register_service: FromDishka[RegisterService]
        ) -> VerificationResponseSchema:
            """
            ## ✉️ Подтверждение email адреса

            Подтверждает email адрес пользователя по токену из письма

            ### Args:
            * **token**: Токен верификации из письма

            ### Returns:
            * Статус подтверждения email
            """
            return await register_service.verify_email(token)
