from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from botocore.client import BaseClient
from app.core.security import PasswordHasher
from app.core.exceptions import ProfileNotFoundError, InvalidCurrentPasswordError, UserNotFoundError
from app.core.integrations.storage.avatars import AvatarS3DataManager
from app.schemas import (ProfileSchema, ProfileResponseSchema,
                         CurrentUserSchema, PasswordUpdateResponseSchema,
                         PasswordFormSchema, AvatarResponseSchema,
                         AvatarDataSchema)
from app.services.v1.base import BaseService

from .data_manager import ProfileDataManager

class ProfileService(BaseService):
    """
    Сервис для работы с профилем пользователя.

    Attributes:
        session: Асинхронная сессия для работы с базой данных."

    """
    def __init__(self, db_session: AsyncSession, s3_client: BaseClient):
        super().__init__(db_session)
        self.data_manager = ProfileDataManager(db_session)
        self.s3_data_manager = AvatarS3DataManager(s3_client)

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

        profile = await self.data_manager.get_item(user.id)

        if profile is None:
            raise ProfileNotFoundError()

        return profile

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
        return await self.data_manager.update_item(user.id, profile_data)

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
        user_model = await self.data_manager.get_item_by_field("id", current_user.id)
        if not user_model:
            raise UserNotFoundError(
                field="id",
                value=current_user.id,
            )

        if not PasswordHasher.verify(user_model.hashed_password, password_data.old_password):
            raise InvalidCurrentPasswordError()

        new_hashed_password = PasswordHasher.hash_password(password_data.new_password)

        success = await self.data_manager.update_fields(
            current_user.id,
            {"hashed_password": new_hashed_password}
        )

        return PasswordUpdateResponseSchema(
            success=success,
            message="Пароль успешно изменен"
        )

    async def get_avatar(self, user: CurrentUserSchema) -> AvatarResponseSchema:
        """
        Получает аватар пользователя.

        Args:
            user: Объект пользователя

        Returns:
            AvatarResponseSchema: Аватар пользователя.
        """
        profile = await self.data_manager.get_item(user.id)
        if not profile.avatar:
            return AvatarResponseSchema(
                data=AvatarDataSchema(
                    url="",
                    alt=f"Аватар пользователя {user.username}"
                ),
                success=False,
                message="Аватар не найден"
            )
        if profile.avatar:
            try:
                file_key = profile.avatar.split(f'{self.s3_data_manager.endpoint}/{self.s3_data_manager.bucket_name}/')[1]
                exists = await self.s3_data_manager.file_exists(file_key)
                if exists:
                    avatar_url = await self.data_manager.get_avatar(user.id)
                    return AvatarResponseSchema(
                                    data=AvatarDataSchema(
                                    url=avatar_url,
                                    alt=f"Аватар пользователя {user.username}"
                                ),
                                message="Аватар успешно обновлен"
                            )
            except Exception as e:
                self.logger.error("Ошибка при проверке аватара: %s", str(e))

        return AvatarResponseSchema(
            data=AvatarDataSchema(
                url="",
                alt=f"Аватар пользователя {user.username}"
            ),
            message="Аватар отсутствует"
        )

    async def update_avatar(self, user: CurrentUserSchema, file: UploadFile) -> AvatarResponseSchema:
        """
        Загружает и обновляет аватар пользователя.

        Args:
            user: Данные текущего пользователя
            file: Загруженный файл аватара

        Returns:
            AvatarResponseSchema: Информация о загруженном аватаре
        """
        profile = await self.data_manager.get_item(user.id)
        old_avatar_url = None
        if profile:
            if hasattr(profile, 'avatar') and profile.avatar:
                old_avatar_url = profile.avatar
                self.logger.info('Текущий аватар: %s', old_avatar_url)
            else:
                self.logger.info('Аватар не установлен')
        else:
            self.logger.warning('Профиль не найден для пользователя %s', user.id)

        avatar_url = await self.s3_data_manager.process_avatar(
            old_avatar_url=old_avatar_url,
            file=file
        )
        self.logger.info('Файл загружен: %s', avatar_url)

        # Обновление аватара в БД
        avatar_data = await self.data_manager.update_avatar(user.id, avatar_url)
        return AvatarResponseSchema(
            data=avatar_data,
            message="Аватар успешно обновлен"
        )
