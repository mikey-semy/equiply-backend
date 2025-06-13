from typing import Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Cookie, Depends, Header, Query, Response
from fastapi.security import OAuth2PasswordRequestForm
from app.core.exceptions import TokenMissingError
from app.routes.base import BaseRouter
from app.schemas import (ForgotPasswordSchema, LogoutResponseSchema,
                         PasswordResetConfirmResponseSchema,
                         PasswordResetConfirmSchema,
                         PasswordResetResponseSchema, TokenResponseSchema)
from app.schemas.v1.auth.exceptions import (InvalidCredentialsResponseSchema,
                                            TokenExpiredResponseSchema,
                                            TokenInvalidResponseSchema,
                                            TokenMissingResponseSchema,
                                            UserInactiveResponseSchema,
                                            WeakPasswordResponseSchema)
from app.schemas.v1.errors import RateLimitExceededResponseSchema
from app.services.v1.auth.service import AuthService


class AuthRouter(BaseRouter):
    """
    Класс для настройки маршрутов аутентификации.

    Этот класс предоставляет маршруты для аутентификации пользователей,
    такие как вход, выход, запрос на восстановление пароля и подтверждение сброса пароля.

    """

    def __init__(self):
        super().__init__(prefix="auth", tags=["Authentication"])

    def configure(self):
        @self.router.post(
            path="",
            response_model=TokenResponseSchema,
            responses={
                401: {
                    "model": InvalidCredentialsResponseSchema,
                    "description": "Неверные учетные данные",
                },
                403: {
                    "model": UserInactiveResponseSchema,
                    "description": "Аккаунт пользователя деактивирован",
                },
                429: {
                    "model": RateLimitExceededResponseSchema,
                    "description": "Превышен лимит запросов",
                },
            },
        )
        @inject
        async def authenticate(
            response: Response,
            auth_service: FromDishka[AuthService],
            use_cookies: bool = Query(
                False, description="Использовать куки для хранения токенов"
            ),
            form_data: OAuth2PasswordRequestForm = Depends(),
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
            * **refresh_token**: Новый refresh токен
            * **token_type**: Тип токена (Bearer)
            """
            return await auth_service.authenticate(form_data, response, use_cookies)

        @self.router.post(
            path="/refresh",
            response_model=TokenResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                419: {
                    "model": TokenExpiredResponseSchema,
                    "description": "Токен просрочен",
                },
                422: {
                    "model": TokenInvalidResponseSchema,
                    "description": "Невалидный токен",
                },
                429: {
                    "model": RateLimitExceededResponseSchema,
                    "description": "Превышен лимит запросов",
                },
            },
        )
        @inject
        async def refresh_token(
            auth_service: FromDishka[AuthService],
            response: Response,
            use_cookies: bool = Query(
                False, description="Использовать куки для токенов"
            ),
            refresh_token_header: str = Header(None, alias="refresh-token"),
            refresh_token_cookie: str = Cookie(None, alias="refresh_token"),
        ) -> TokenResponseSchema:
            """
            ## 🔄 Обновление токена доступа

            Получение нового access токена с помощью refresh токена.

            ### Заголовки:
            * **refresh_token**: Refresh токен, полученный при аутентификации

            ### Returns:
            * **access_token**: Новый JWT токен доступа
            * **refresh_token**: Новый refresh токен
            * **token_type**: Тип токена (Bearer)
            """
            # Приоритет: заголовок -> кука
            refresh_token = refresh_token_header or refresh_token_cookie

            if not refresh_token:
                raise TokenMissingError()

            return await auth_service.refresh_token(refresh_token, response, use_cookies)

        @self.router.post(
            path="/logout",
            response_model=LogoutResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                419: {
                    "model": TokenExpiredResponseSchema,
                    "description": "Токен просрочен",
                },
                422: {
                    "model": TokenInvalidResponseSchema,
                    "description": "Невалидный токен",
                },
                429: {
                    "model": RateLimitExceededResponseSchema,
                    "description": "Превышен лимит запросов",
                },
            },
        )
        @inject
        async def logout(
            auth_service: FromDishka[AuthService],
            response: Response,
            clear_cookies: bool = Query(False, description="Очистить куки при выходе"),
            authorization: str = Header(None, description="Токен доступа"),
            access_token_cookie: str = Cookie(None, alias="access_token"),
        ) -> LogoutResponseSchema:
            """
            ## 🚪 Выход из системы

            Выход пользователя из системы и инвалидация токена.

            ### Заголовки:
            * **Authorization**: Bearer токен для аутентификации

            ### Returns:
            * **success**: Флаг успешности операции (всегда true)
            * **message**: Сообщение о результате операции ("Выход выполнен успешно!")
            """
            if not authorization and access_token_cookie:
                authorization = f"Bearer {access_token_cookie}"

            return await auth_service.logout(authorization, response, clear_cookies)

        @self.router.post(
            path="/forgot-password", response_model=PasswordResetResponseSchema
        )
        @inject
        async def forgot_password(
            email_data: ForgotPasswordSchema, auth_service: FromDishka[AuthService]
        ) -> PasswordResetResponseSchema:
            """
            ## 📧 Запрос на восстановление пароля

            Отправляет ссылку для восстановления пароля на указанный email

            ### Args:
            * **email**: Email-адрес, привязанный к учетной записи

            ### Returns:
            * Статус отправки письма для восстановления пароля
            """
            return await auth_service.send_password_reset_email(email_data.email)

        @self.router.post(
            path="/reset-password/{token}",
            response_model=PasswordResetConfirmResponseSchema,
            responses={
                400: {
                    "model": WeakPasswordResponseSchema,
                    "description": "Слабый пароль",
                },
                419: {
                    "model": TokenExpiredResponseSchema,
                    "description": "Токен сброса пароля истек",
                },
                422: {
                    "model": TokenInvalidResponseSchema,
                    "description": "Недействительный токен сброса пароля",
                },
                429: {
                    "model": RateLimitExceededResponseSchema,
                    "description": "Превышен лимит запросов",
                },
            },
        )
        @inject
        async def reset_password(
            token: str,
            password_data: PasswordResetConfirmSchema,
            auth_service: FromDishka[AuthService],
        ) -> PasswordResetConfirmResponseSchema:
            """
            ## 🔄 Сброс пароля

            Устанавливает новый пароль пользователя по токену сброса пароля

            ### Args:
            * **token**: Токен сброса пароля из email-сообщения (path parameter)
            * **password**: Новый пароль пользователя (в теле запроса)

            ### Returns:
            * Статус операции сброса пароля
            """
            return await auth_service.reset_password(token, password_data.password)
