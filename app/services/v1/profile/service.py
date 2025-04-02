"""
Сервис для работы с профилем пользователя.
"""
import random
from typing import Optional
from botocore.exceptions import ClientError  # type: ignore
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (FileTooLargeError,
                                 InvalidCurrentPasswordError,
                                 InvalidFileTypeError, ProfileNotFoundError,
                                 StorageError, UserNotFoundError)
from app.core.integrations.storage.avatars import AvatarS3DataManager
from app.core.utils.username_generator import UsernameGenerator, UsernameTheme
from app.core.utils.password_generator import generate_secure_password
from app.core.security import PasswordHasher
from app.schemas import (AvatarDataSchema, AvatarResponseSchema,
                         CurrentUserSchema, PasswordFormSchema,
                         PasswordUpdateResponseSchema, ProfileResponseSchema,
                         ProfileUpdateSchema, UsernameDataSchema, 
                         UsernameResponseSchema, PasswordDataSchema)
from app.services.v1.base import BaseService

from .data_manager import ProfileDataManager


class ProfileService(BaseService):
    """
    Сервис для работы с профилем пользователя.

    Attributes:
        session: Асинхронная сессия для работы с базой данных."

    """

    def __init__(
        self,
        db_session: AsyncSession,
        s3_data_manager: Optional[AvatarS3DataManager] = None
    ):
        super().__init__(db_session)
        self.data_manager = ProfileDataManager(db_session)
        self.s3_data_manager = s3_data_manager
        self.username_generator = UsernameGenerator()

    async def get_profile(self, user: CurrentUserSchema) -> ProfileResponseSchema:
        """
        Получает профиль пользователя по ID пользователя.

        Args:
            user: (CurrentUserSchema) Объект пользователя

        Returns:
            ProfileResponseSchema: Профиль пользователя.
        """

        profile_data = await self.data_manager.get_item(user.id)

        if profile_data is None:
            raise ProfileNotFoundError()

        return ProfileResponseSchema(data=profile_data)

    async def update_profile(
        self, user: CurrentUserSchema, profile_data: ProfileUpdateSchema
    ) -> ProfileResponseSchema:
        """
        Обновляет профиль пользователя.

        Args:
            user: Объект пользователя
            profile_data (ProfileUpdateSchema): Данные профиля пользователя.

        Returns:
            ProfileResponseSchema: Обновленный профиль пользователя.
        """
        update_data = profile_data.model_dump(exclude_unset=True)

        updated_profile = await self.data_manager.update_items(user.id, update_data)

        return ProfileResponseSchema(
            message="Данные профиля успешно обновлены",
            data=updated_profile
        )

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
        user_model = await self.data_manager.get_model_by_field("id", current_user.id)
        if not user_model:
            raise UserNotFoundError(
                field="id",
                value=current_user.id,
            )

        if not PasswordHasher.verify(
            user_model.hashed_password, password_data.old_password
        ):
            raise InvalidCurrentPasswordError()

        new_hashed_password = PasswordHasher.hash_password(password_data.new_password)

        await self.data_manager.update_items(
            current_user.id, {"hashed_password": new_hashed_password}
        )

        return PasswordUpdateResponseSchema()

    async def get_avatar(self, user: CurrentUserSchema) -> AvatarResponseSchema:
        """
        Получает аватар пользователя.

        Args:
            user: Объект пользователя

        Returns:
            AvatarResponseSchema: Аватар пользователя.
        """
        profile = await self.data_manager.get_item(user.id)
        if not profile or not profile.avatar:
            return AvatarResponseSchema(
                data=AvatarDataSchema(
                    url="", alt=f"Аватар пользователя {user.username}"
                ),
                success=False,
                message="Аватар не найден",
            )

        try:
            file_key = profile.avatar.split(
                f"{self.s3_data_manager.endpoint}/{self.s3_data_manager.bucket_name}/"
            )[1]
            exists = await self.s3_data_manager.file_exists(file_key)
            if exists:
                avatar_url = profile.avatar
                return AvatarResponseSchema(
                    data=AvatarDataSchema(
                        url=avatar_url, alt=f"Аватар пользователя {user.username}"
                    ),
                    message="Аватар успешно получен",
                )
        except Exception as e:
            self.logger.error("Ошибка при проверке аватара: %s", str(e))

        return AvatarResponseSchema(
            data=AvatarDataSchema(url="", alt=f"Аватар пользователя {user.username}"),
            message="Аватар отсутствует",
        )

    async def update_avatar(
        self, user: CurrentUserSchema, file: UploadFile
    ) -> AvatarResponseSchema:
        """
        Загружает и обновляет аватар пользователя.

        Args:
            user: Данные текущего пользователя
            file: Загруженный файл аватара

        Returns:
            AvatarResponseSchema: Информация о загруженном аватаре

        Raises:
            ProfileNotFoundError: Если профиль пользователя не найден
            InvalidFileTypeError: Если тип файла не поддерживается
            FileTooLargeError: Если размер файла превышает лимит
            StorageError: Если произошла ошибка при загрузке файла в хранилище
        """
        # Проверка размера и типа файла
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > 2_000_000:  # 2MB
            raise FileTooLargeError()

        # Проверка типа файла (дополнительно к проверке FastAPI)
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise InvalidFileTypeError()

        profile = await self.data_manager.get_item(user.id)
        if not profile:
            raise ProfileNotFoundError()

        old_avatar_url = None
        if hasattr(profile, "avatar") and profile.avatar:
            old_avatar_url = profile.avatar
            self.logger.info("Текущий аватар: %s", old_avatar_url)
        else:
            self.logger.info("Аватар не установлен")

        try:
            avatar_url = await self.s3_data_manager.process_avatar(
                old_avatar_url=old_avatar_url if old_avatar_url else "",
                file=file,
                file_content=file_content,
            )
            self.logger.info("Файл загружен: %s", avatar_url)
        except ClientError as e:
            self.logger.error("Ошибка S3 при загрузке аватара: %s", str(e))
            raise StorageError(detail=f"Ошибка хранилища: {str(e)}")
        except ValueError as e:
            self.logger.error("Ошибка валидации при загрузке аватара: %s", str(e))
            raise StorageError(detail=str(e))
        except Exception as e:
            self.logger.error("Неизвестная ошибка при загрузке аватара: %s", str(e))
            raise StorageError(detail=f"Ошибка при загрузке аватара: {str(e)}")

        # Обновление аватара в БД
        avatar_data = await self.data_manager.update_avatar(user.id, avatar_url)
        return AvatarResponseSchema(data=avatar_data, message="Аватар успешно обновлен")

    async def delete_avatar(self, user: CurrentUserSchema) -> AvatarResponseSchema:
        """
        Удаляет аватар пользователя.

        Args:
            user: Объект пользователя

        Returns:
            AvatarResponseSchema: Информация о результате операции

        Raises:
            ProfileNotFoundError: Если профиль пользователя не найден
            StorageError: Если произошла ошибка при удалении файла из хранилища
        """
        # Получаем профиль пользователя
        profile = await self.data_manager.get_item(user.id)
        if not profile:
            raise ProfileNotFoundError()

        # Проверяем, есть ли аватар для удаления
        if not profile.avatar:
            return AvatarResponseSchema(
                data=AvatarDataSchema(url="", alt=f"Аватар пользователя {user.username}"),
                message="Аватар отсутствует",
                success=False
            )

        # Удаляем файл из S3, если он существует
        try:
            if self.s3_data_manager:
                # Извлекаем ключ файла из полного URL
                file_key = profile.avatar.split(
                    f"{self.s3_data_manager.endpoint}/{self.s3_data_manager.bucket_name}/"
                )[1]

                # Проверяем существование файла перед удалением
                exists = await self.s3_data_manager.file_exists(file_key)
                if exists:
                    await self.s3_data_manager.delete_file(file_key)
                    self.logger.info("Файл аватара удален из хранилища: %s", file_key)
        except Exception as e:
            self.logger.error("Ошибка при удалении аватара из хранилища: %s", str(e))
            raise StorageError(detail=f"Ошибка при удалении аватара: {str(e)}")

        # Обновляем запись в БД, устанавливая avatar в NULL
        try:
            await self.data_manager.update_items(user.id, {"avatar": None})
            self.logger.info("Аватар пользователя %s удален из БД", user.id)
        except Exception as e:
            self.logger.error("Ошибка при удалении аватара из БД: %s", str(e))
            raise StorageError(detail=f"Ошибка при обновлении данных: {str(e)}")

        return AvatarResponseSchema(
            data=AvatarDataSchema(url="", alt=f"Аватар пользователя {user.username}"),
            message="Аватар успешно удален",
            success=True
        )

    async def generate_username(self, theme: Optional[UsernameTheme] = None) -> UsernameDataSchema:
        """
        Генерирует уникальное имя пользователя.

        Args:
            theme: Тема для генерации имени пользователя

        Returns:
            UsernameDataSchema: Сгенерированное имя пользователя
        """
        if theme is None:
            theme = UsernameTheme.RANDOM

        # Пробуем получить имена от AI
        try:
            usernames = await self.username_generator.generate_username_with_ai(theme)

            # Перемешиваем список имен для случайного порядка
            random.shuffle(usernames)

            # Проверяем каждое имя на уникальность
            for username in usernames:
                existing_user = await self.data_manager.get_model_by_field("username", username)
                if not existing_user:
                    return UsernameDataSchema(username=username)

            # Если все имена заняты, добавляем случайное число
            random_username = random.choice(usernames)
            random_number = random.randint(1000, 9999)
            username = f"{random_username}_{random_number}"

            # Проверяем еще раз
            existing_user = await self.data_manager.get_model_by_field("username", username)
            if not existing_user:
                return UsernameDataSchema(username=username)

        except Exception as e:
            self.logger.error(f"Ошибка при генерации имени пользователя: {e}")

        # Если что-то пошло не так, используем запасной вариант
        for _ in range(5):  # Максимум 5 попыток
            username = self.username_generator.get_fallback_username(theme)
            existing_user = await self.data_manager.get_model_by_field("username", username)
            if not existing_user:
                return UsernameDataSchema(username=username)

        # Если все попытки не удались, используем timestamp
        import time
        timestamp = int(time.time())
        return UsernameDataSchema(username=f"user_{timestamp}")

    async def generate_password(self) -> PasswordDataSchema:
        """
        Генерирует надежный пароль, соответствующий требованиям безопасности.

        Returns:
            str: Сгенерированный пароль
        """
        password = generate_secure_password()
        return PasswordDataSchema(password=password)
