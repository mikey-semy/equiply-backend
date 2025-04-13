import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.v1.users.base import UserRole
from app.services.v1.users.data_manager import UserDataManager

logger = logging.getLogger(__name__)


class AdminInitService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.data_manager = UserDataManager(db_session)

    async def initialize_admin(self, admin_email: str):
        # Проверяем, есть ли уже администраторы
        admins = await self.data_manager.get_items_by_field(
            "role", UserRole.ADMIN.value
        )
        logger.debug("Администраторы: %s", admins)
        if not admins:
            # Ищем пользователя с указанным email
            user = await self.data_manager.get_item_by_field("email", admin_email)
            logger.debug("Пользователь: %s", user)
            if user:
                # Назначаем роль администратора
                try:
                    updated_user = await self.data_manager.assign_role(
                        user.id, UserRole.ADMIN
                    )
                    if updated_user:
                        logger.info(
                            "Пользователь с email %s назначен администратором",
                            admin_email,
                        )
                except Exception as e:
                    logger.error("Не удалось назначить роль администратора: %s", str(e))
            else:
                logger.warning("Пользователь с email %s не найден", admin_email)
        else:
            logger.info("Количество администраторов в системе: %s", len(admins))
