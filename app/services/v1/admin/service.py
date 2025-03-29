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
        admins = await self.data_manager.get_items_by_field("role", UserRole.ADMIN.value)
        logger.debug(f"Администраторы: {admins}")
        if not admins:
            # Ищем пользователя с указанным email
            user = await self.data_manager.get_item_by_field("email", admin_email)
            logger.debug(f"Пользователь: {user}")
            if user:
                # Назначаем роль администратора
                try:
                    updated_user = await self.data_manager.assign_role(user.id, UserRole.ADMIN)
                    if updated_user:
                        logger.info(f"Пользователь с email {admin_email} назначен администратором")
                except Exception as e:
                    logger.error(f"Не удалось назначить роль администратора: {str(e)}")
            else:
                logger.warning(f"Пользователь с email {admin_email} не найден")
        else:
            logger.info(f"Количество администраторов в системе: {len(admins)}")
