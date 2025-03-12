from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import InvalidCurrentPasswordError, UserNotFoundError
from app.schemas import ProfileSchema, ProfileResponseSchema, CurrentUserSchema
from app.services.v1.base import BaseService

from .data_manager import AvatarDataManager

class AvatarService(BaseService):
    """
    Сервис для работы с аватаром пользователя.

    Attributes:
        session: Асинхронная сессия для работы с базой данных."
    
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._data_manager = AvatarDataManager(session)
    
    async def get_avatar(self, user: UserSchema) -> AvatarSchema:
        """
        Получает аватар пользователя.

        Args:
            user: Объект пользователя
            session (AsyncSession): Асинхронная сессия базы данных.

        Returns:
            AvatarSchema: Аватар пользователя.
        """
        current_profile = await self.get_profile(user)
        if current_profile.avatar:
            try:
                file_key = current_profile.avatar.split(f'{self.s3_manager.endpoint}/{self.s3_manager.bucket_name}/')[1]
                exists = await self.s3_manager.file_exists(file_key)
                if exists:
                    avatar_url = await self.profile_manager.get_avatar(user.id)
                    return AvatarSchema(url=avatar_url)
            except Exception:
                pass
        return AvatarSchema(url='')
    
    async def update_avatar(self, user: UserSchema, file: UploadFile) -> ProfileSchema:
        """
        Обновляет аватар пользователя.

        Args:
            user: Объект пользователя
            file (str): Аватар пользователя.
            session (AsyncSession): Асинхронная сессия базы данных.

        Returns:
            ProfileSchema: Обновленный профиль пользователя.
        """
        current_profile = await self.get_profile(user)
        logging.info('Текущий аватар: %s', current_profile.avatar)
        if current_profile.avatar:
            try:
                old_file_key = current_profile.avatar.split(f'{self.s3_manager.endpoint}/{self.s3_manager.bucket_name}/')[1]
                logging.info('Удаляем файл: %s', old_file_key)
                if await self.s3_manager.file_exists(old_file_key):
                    logging.info('Файл существует, начинаем процесс удаления')
                    await self.s3_manager.delete_file(old_file_key)
                    logging.info('Файл удален')
            except Exception:
                logging.error('Ошибка удаления файла')
        logging.info('Загружаем новый файл')
        # avatar_url = await self.s3_operations.process_avatar(current_profile.avatar, file)
        avatar_url = await self.s3_manager.upload_file_from_content(
            file=file,
            file_key="avatars"
        )
        logging.info('Файл загружен: %s', avatar_url)
        return await self.profile_manager.update_avatar(user.id, avatar_url)