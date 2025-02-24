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
# from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
# from starlette.exceptions import HTTPException
# from starlette.websockets import WebSocketDisconnect

from app.routes.v1.api import APIv1
from app.routes.main import MainRouter
from app.core.settings import settings
# from app.core.exceptions import AuthenticationError, BaseAPIException
# from app.core.handlers import (api_exception_handler, auth_exception_handler,
#                                http_exception_handler,
#                                internal_exception_handler,
#                                validation_exception_handler,
#                                websocket_exception_handler)
# from app.core.middlewares.auth import LastActivityMiddleware
from app.core.middlewares.docs_auth import DocsAuthMiddleware
from app.core.middlewares.logging import LoggingMiddleware
# from app.routes import all_routes

# Создаем FastAPI приложение с параметрами из конфига
app = FastAPI(**settings.app_params)

# Добавляем обработчик исключений
# app.add_exception_handler(BaseAPIException, api_exception_handler)
# app.add_exception_handler(HTTPException, http_exception_handler)
# app.add_exception_handler(RequestValidationError, validation_exception_handler)
# app.add_exception_handler(WebSocketDisconnect, websocket_exception_handler)
# app.add_exception_handler(AuthenticationError, auth_exception_handler)
# app.add_exception_handler(Exception, internal_exception_handler)

# Добавляем middleware в порядке выполнения
app.add_middleware(LoggingMiddleware)  # Логирование запросов
app.add_middleware(DocsAuthMiddleware)  # Защита документации
app.add_middleware(CORSMiddleware, **settings.cors_params)  # CORS политики
# app.add_middleware(LastActivityMiddleware)

# Подключаем все маршруты
# app.include_router(all_routes())

# Базовые роутеры без версий
app.include_router(MainRouter().get_router())

# API с версиями
v1_router = APIv1()
v1_router.configure_routes()
app.include_router(v1_router.get_router(), prefix="/api/v1")

# Запуск через uvicorn при прямом вызове файла
if __name__ == "__main__":
    uvicorn.run(app, **settings.uvicorn_params)
