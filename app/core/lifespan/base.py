import logging
from contextlib import asynccontextmanager
from typing import List, Callable, Awaitable

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
    for handler in startup_handlers:
        try:
            logger.info(f"Запуск обработчика: {handler.__name__}")
            await handler(app)
        except Exception as e:
            logger.error(f"Ошибка в обработчике {handler.__name__}: {str(e)}")

async def run_shutdown_handlers(app: FastAPI):
    """Запускает все зарегистрированные обработчики остановки"""
    for handler in shutdown_handlers:
        try:
            logger.info(f"Запуск обработчика остановки: {handler.__name__}")
            await handler(app)
        except Exception as e:
            logger.error(f"Ошибка в обработчике остановки {handler.__name__}: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер жизненного цикла приложения"""
    # Запускаем все обработчики старта
    await run_startup_handlers(app)

    yield

    # Запускаем все обработчики остановки
    await run_shutdown_handlers(app)
