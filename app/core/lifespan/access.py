import logging

from fastapi import FastAPI

from app.core.dependencies.container import container
from app.core.lifespan.base import register_startup_handler
from app.services.v1.access.init import PolicyInitService
from app.core.settings import settings

logger = logging.getLogger("app.lifecycle.policies")


@register_startup_handler
async def initialize_default_policies(app: FastAPI):
    """
    Инициализация базовых политик доступа при старте приложения.

    Загружает политики из JSON-файлов и создает их в базе данных,
    если они еще не существуют.
    """
    logger.info("Инициализация базовых политик доступа")

    # Проверяем наличие директории с политиками
    policies_dir = settings.paths.POLICIES_DIR
    if not policies_dir.exists():
        logger.warning("Директория с политиками не найдена: %s", policies_dir)
        return

    # Получаем сервис инициализации политик через контейнер зависимостей
    async with container() as request_container:
        policy_init_service = await request_container.get(PolicyInitService)

        # Загружаем и создаем политики
        total_created = await policy_init_service.initialize_default_policies(
            policies_dir
        )

        if total_created > 0:
            logger.info(
                "Инициализация базовых политик завершена. Создано %s политик",
                total_created
            )
        else:
            logger.info("Базовые политики уже существуют или не были созданы")
