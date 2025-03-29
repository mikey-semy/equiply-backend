import logging
from fastapi import FastAPI

from app.core.lifespan.base import register_startup_handler

logger = logging.getLogger("app.lifecycle.admin")

@register_startup_handler
async def initialize_admin(app: FastAPI):
    """Инициализация администратора при старте приложения"""

    from app.core.dependencies.container import container
    from app.services.v1.admin.service import AdminInitService
    from app.core.settings import settings

    admin_email = settings.ADMIN_EMAIL
    if not admin_email:
        logger.info("ADMIN_EMAIL не указан в настройках, пропускаем создание администратора")
        return

    async with container() as request_container:
        admin_service = await request_container.get(AdminInitService)
        await admin_service.initialize_admin(admin_email)
