"""
Главный модуль приложения.

Инициализирует FastAPI приложение с:
- Подключением всех роутов
- Настройкой CORS
- Middleware для логирования
- Защитой документации
- Параметрами запуска uvicorn
"""

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.websockets import WebSocketDisconnect

from app.routes.v1 import APIv1
from app.routes.main import MainRouter
from app.core.settings import settings
from app.core.exceptions import AuthenticationError, BaseAPIException
from app.core.exceptions.handlers import (api_exception_handler, auth_exception_handler,
                               http_exception_handler,
                               internal_exception_handler,
                               validation_exception_handler,
                               websocket_exception_handler)
from app.core.middlewares.auth import LastActivityMiddleware
from app.core.middlewares.docs_auth import DocsAuthMiddleware
from app.core.middlewares.logging import LoggingMiddleware
from dishka.integrations.fastapi import setup_dishka
from app.core.dependencies.container import container

def create_application() -> FastAPI:
    """
    Создает и настраивает экземпляр приложения FastAPI.
    """
    app = FastAPI(**settings.app_params)
    
    setup_dishka(container=container, app=app)
    
    app.add_exception_handler(BaseAPIException, api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(WebSocketDisconnect, websocket_exception_handler)
    app.add_exception_handler(AuthenticationError, auth_exception_handler)
    app.add_exception_handler(Exception, internal_exception_handler)

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(DocsAuthMiddleware)
    app.add_middleware(CORSMiddleware, **settings.cors_params)
    app.add_middleware(LastActivityMiddleware)

    app.include_router(MainRouter().get_router())

    v1_router = APIv1()
    v1_router.configure_routes()
    app.include_router(v1_router.get_router(), prefix="/api/v1")
    
    return app

app = create_application()

if __name__ == "__main__":
    uvicorn.run(app, **settings.uvicorn_params)
