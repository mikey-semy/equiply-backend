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
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.dependencies.container import container
from app.core.exceptions.handlers import register_exception_handlers
from app.core.integrations.messaging.setup import setup_messaging
from app.core.logging import setup_logging
from app.core.middlewares.rate_limit import RateLimitMiddleware
from app.core.middlewares.activity import ActivityMiddleware
from app.core.middlewares.docs_auth import DocsAuthMiddleware
from app.core.middlewares.logging import LoggingMiddleware
from app.core.settings import settings
from app.routes.main import MainRouter
from app.routes.v1 import APIv1


def create_application() -> FastAPI:
    """
    Создает и настраивает экземпляр приложения FastAPI.
    """
    app = FastAPI(**settings.app_params)
    setup_logging()
    setup_dishka(container=container, app=app)

    register_exception_handlers(app=app)

    app.add_middleware(ActivityMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(DocsAuthMiddleware)
    app.add_middleware(CORSMiddleware, **settings.cors_params)
    app.add_middleware(RateLimitMiddleware,**settings.rate_limit_params)

    app.include_router(MainRouter().get_router())

    v1_router = APIv1()
    v1_router.configure_routes()
    app.include_router(v1_router.get_router(), prefix="/api/v1")

    setup_messaging(app)

    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run(app, **settings.uvicorn_params)
