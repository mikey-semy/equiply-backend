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
            ## 🔐 Аутентификация пользователя
            
            Аутентифицирует пользователя по имени, email или телефону
            
            ### Для аутентификации используйте один из вариантов:
            * Email-адрес
            * Имя пользователя
            * Телефон в формате +7 (XXX) XXX-XX-XX
            
            ### Returns:
            * **access_token**: JWT токен доступа
            * **token_type**: Тип токена (Bearer)
            """
            return await auth_service.authenticate(form_data)

        @self.router.post("/logout")
        @inject
        async def logout(
            token: str,
            auth_service: FromDishka[AuthService]
        ) -> dict:
            """
            ## 👋 Выход из системы
            
            Выполняет выход из системы, делая текущий токен недействительным
            
            ### Parameters:
            * **token**: Действующий JWT токен пользователя
            
            ### Returns:
            * Статус операции
            """
            return await auth_service.logout(token)

        @self.router.post("/forgot-password", response_model=PasswordResetResponseSchema)
        @inject
        async def forgot_password(
            email_data: ForgotPasswordSchema,
            auth_service: FromDishka[AuthService]
        ) -> PasswordResetResponseSchema:
            """
            ## 📧 Запрос на восстановление пароля
            
            Отправляет ссылку для восстановления пароля на указанный email
            
            ### Parameters:
            * **email**: Email-адрес, привязанный к учетной записи
            
            ### Returns:
            * Статус отправки письма для восстановления пароля
            """
            return await auth_service.send_password_reset_email(email_data.email)

        @self.router.post("/reset-password/{token}", response_model=PasswordResetConfirmResponseSchema)
        @inject
        async def reset_password(
            token: str,
            password_data: PasswordResetConfirmSchema,
            auth_service: FromDishka[AuthService]
        ) -> PasswordResetConfirmResponseSchema:
            """
            ## 🔄 Сброс пароля
            
            Устанавливает новый пароль пользователя по токену сброса пароля
            
            ### Parameters:
            * **token**: Токен сброса пароля из email-сообщения (path parameter)
            * **password**: Новый пароль пользователя (в теле запроса)
            
            ### Returns:
            * Статус операции сброса пароля
            """
            return await auth_service.reset_password(token, password_data.password)