from typing import Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi.responses import RedirectResponse

from app.routes.base import BaseRouter
from app.schemas import OAuthProvider, OAuthResponseSchema
from app.services.v1.oauth.service import OAuthService


class OAuthRouter(BaseRouter):
    """
    Класс для настройки маршрутов OAuth2 аутентификации.
    """

    def __init__(self):
        super().__init__(prefix="oauth", tags=["OAuthentication"])

    def configure(self):
        @self.router.get(
            path="/{provider}",
            response_class=RedirectResponse,
        )
        @inject
        async def get_oauth_url(
            oauth_service: FromDishka[OAuthService],
            provider: OAuthProvider,
        ) -> RedirectResponse:
            """
            🌐 **Редирект на страницу авторизации провайдера.**

            **Args**:
            - **provider**: Имя провайдера (vk/google/yandex)

            **Returns**:
            - **RedirectResponse**: Редирект на страницу авторизации
            """
            return await oauth_service.get_oauth_url(provider)

        @self.router.get(
            path="/{provider}/callback",
            response_model=OAuthResponseSchema,
        )
        @inject
        async def oauth_callback(
            oauth_service: FromDishka[OAuthService],
            provider: OAuthProvider,
            code: str,
            state: Optional[str] = None,
            device_id: Optional[str] = None,
        ) -> OAuthResponseSchema:
            """
            🔄 **Обработка ответа от OAuth провайдера.**

            **Args**:
            - **provider**: Имя провайдера
            - **code**: Код авторизации от провайдера

            **Returns**:
            - **OAuthResponse**: Токен доступа
            """
            return await oauth_service.authenticate(provider, code, state, device_id)
