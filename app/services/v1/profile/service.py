from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import PasswordHasher
from app.core.exceptions import InvalidCurrentPasswordError, UserNotFoundError
from app.schemas import ProfileSchema, ProfileResponseSchema, CurrentUserSchema, PasswordUpdateResponseSchema, PasswordFormSchema
from app.services.v1.base import BaseService

from .data_manager import ProfileDataManager

class ProfileService(BaseService):
    """
    Сервис для работы с профилем пользователя.

    Attributes:
        session: Асинхронная сессия для работы с базой данных."
    
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._data_manager = ProfileDataManager(session)

    async def get_profile(
        self, user: CurrentUserSchema
    ) -> ProfileResponseSchema:
        """
        Получает профиль пользователя по ID пользователя.

        Args:
            user: (CurrentUserSchema) Объект пользователя

        Returns:
            ProfileSchema: Профиль пользователя.
        """

        return await self._data_manager.get_item(user.id)

    async def update_profile(
        self, user: CurrentUserSchema, profile_data: ProfileSchema
    ) -> ProfileResponseSchema:
        """
        Обновляет профиль пользователя.

        Args:
            user: Объект пользователя
            profile_data (ProfileSchema): Данные профиля пользователя.
            session (AsyncSession): Асинхронная сессия базы данных.

        Returns:
            ProfileSchema: Обновленный профиль пользователя.
        """
        return await self.profile_manager.update_item(user.id, profile_data)
    
    async def update_password(
        self, current_user: CurrentUserSchema, password_data: PasswordFormSchema
    ) -> PasswordUpdateResponseSchema:
        """
        Обновляет пароль пользователя.

        Args:
            current_user: (CurrentUserSchema) Объект пользователя
            password_data (PasswordFormSchema): Данные нового пароля пользователя.

        Returns:
            PasswordUpdateResponseSchema: Объект с полями:
            - success (bool): Статус успешного обновления пароля
            - message (str): Сообщение о результате операции

        Raises:
            InvalidCurrentPasswordError: Если текущий пароль неверен
            UserNotFoundError: Если пользователь не найден
        """
        user_model = await self._data_manager.get_item_by_field("id", current_user.id)
        if not user_model:
            raise UserNotFoundError(
                field="id",
                value=current_user.id,
            )
    
        if not PasswordHasher.verify(user_model.hashed_password, password_data.old_password):
            raise InvalidCurrentPasswordError()
    
        new_hashed_password = PasswordHasher.hash_password(password_data.new_password)

        success = await self._data_manager.update_fields(
            current_user.id, 
            {"hashed_password": new_hashed_password}
        )

        return PasswordUpdateResponseSchema(
            success=success,
            message="Пароль успешно изменен"
        )