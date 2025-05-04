import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable, List

from fastapi import FastAPI

logger = logging.getLogger("app.lifecycle")

# Типы для инициализаторов и деструкторов
StartupHandler = Callable[[FastAPI], Awaitable[None]]
ShutdownHandler = Callable[[FastAPI], Awaitable[None]]

# Списки обработчиков
startup_handlers: List[StartupHandler] = []
shutdown_handlers: List[ShutdownHandler] = []


def register_startup_handler(handler: StartupHandler):
    """Регистрирует обработчик для запуска при старте приложения"""
    startup_handlers.append(handler)
    return handler


def register_shutdown_handler(handler: ShutdownHandler):
    """Регистрирует обработчик для запуска при остановке приложения"""
    shutdown_handlers.append(handler)
    return handler


async def run_startup_handlers(app: FastAPI):
    """Запускает все зарегистрированные обработчики старта"""
    from app.core.lifespan.access import initialize_default_policies
    from app.core.lifespan.admin import initialize_admin
    from app.core.lifespan.clients import initialize_clients

    if initialize_default_policies not in startup_handlers:
        startup_handlers.append(initialize_default_policies)
    if initialize_admin not in startup_handlers:
        startup_handlers.append(initialize_admin)
    if initialize_clients not in startup_handlers:
        startup_handlers.append(initialize_clients)

    for handler in startup_handlers:
        try:
            logger.info("Запуск обработчика: %s", handler.__name__)
            await handler(app)
        except Exception as e:
            logger.error("Ошибка в обработчике %s: %s", handler.__name__, str(e))


async def run_shutdown_handlers(app: FastAPI):
    """Запускает все зарегистрированные обработчики остановки"""
    from app.core.lifespan.clients import close_clients

    if close_clients not in shutdown_handlers:
        shutdown_handlers.append(close_clients)

    for handler in shutdown_handlers:
        try:
            logger.info("Запуск обработчика остановки: %s", handler.__name__)
            await handler(app)
        except Exception as e:
            logger.error(
                "Ошибка в обработчике остановки %s: %s", handler.__name__, str(e)
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер жизненного цикла приложения"""
    # Запускаем все обработчики старта
    await run_startup_handlers(app)

    yield

    # Запускаем все обработчики остановки
    await run_shutdown_handlers(app)
