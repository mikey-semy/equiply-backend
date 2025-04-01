from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, File, UploadFile, Query

from app.core.security.auth import get_current_user
from app.core.utils.username_generator import UsernameTheme
from app.routes.base import BaseRouter
from app.schemas import (AvatarResponseSchema, CurrentUserSchema,
                         PasswordFormSchema, PasswordUpdateResponseSchema,
                         ProfileResponseSchema, ProfileUpdateSchema,
                         PasswordResponseSchema, UsernameResponseSchema)
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.schemas.v1.profile.exceptions import (
    FileTooLargeResponseSchema, InvalidCurrentPasswordResponseSchema,
    InvalidFileTypeResponseSchema, ProfileNotFoundResponseSchema,
    StorageErrorResponseSchema, UserNotFoundResponseSchema)
from app.services.v1.profile.service import ProfileService


class ProfileRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="profile", tags=["Profile"])

    def configure(self):
        @self.router.get(path="", response_model=ProfileResponseSchema)
        @inject
        async def get_profile(
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> ProfileResponseSchema:
            """
            ## 👤 Получение профиля пользователя

            Возвращает данные профиля текущего авторизованного пользователя

            ### Returns:
            * **ProfileResponseSchema**: Полная информация о профиле пользователя
            """
            return await profile_service.get_profile(current_user)

        @self.router.put(
            path="",
            response_model=ProfileResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                404: {
                    "model": ProfileNotFoundResponseSchema,
                    "description": "Профиль не найден",
                },
            },
        )
        @inject
        async def update_profile(
            profile_data: ProfileUpdateSchema,
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> ProfileResponseSchema:
            """
            ## ✏️ Обновление профиля пользователя

            Изменяет основные данные профиля текущего пользователя

            ### Args:
            * **username**: Имя пользователя (опционально)
            * **email**: Email пользователя (опционально)
            * **phone**: Телефон пользователя в формате +7 (XXX) XXX-XX-XX (опционально)

            ### Returns:
            * **ProfileResponseSchema**: Обновленная информация о профиле пользователя
            """
            return await profile_service.update_profile(current_user, profile_data)

        @self.router.put(
            path="/password",
            response_model=PasswordUpdateResponseSchema,
            responses={
                400: {
                    "model": InvalidCurrentPasswordResponseSchema,
                    "description": "Текущий пароль неверен",
                },
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден",
                },
            },
        )
        @inject
        async def update_password(
            profile_service: FromDishka[ProfileService],
            password_data: PasswordFormSchema,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> PasswordUpdateResponseSchema:
            """
            ## 🔄 Обновление пароля пользователя

            Изменяет пароль текущего пользователя

            ### Args:
            * **old_password**: Текущий пароль
            * **new_password**: Новый пароль
            * **confirm_password**: Подтверждение нового пароля

            ### Returns:
            * Статус операции изменения пароля
            """
            return await profile_service.update_password(current_user, password_data)

        @self.router.get(
            path="/avatar",
            response_model=AvatarResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                404: {
                    "model": ProfileNotFoundResponseSchema,
                    "description": "Профиль не найден",
                },
            },
        )
        @inject
        async def get_avatar(
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AvatarResponseSchema:
            """
            ## 🖼️ Получение аватара пользователя

            Возвращает URL аватара текущего пользователя

            ### Returns:
            * **AvatarResponseSchema**: URL-адрес аватара пользователя
            """
            return await profile_service.get_avatar(current_user)

        @self.router.post(
            path="/avatar",
            response_model=AvatarResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                413: {
                    "model": FileTooLargeResponseSchema,
                    "description": "Размер файла превышает допустимый лимит (2MB)",
                },
                415: {
                    "model": InvalidFileTypeResponseSchema,
                    "description": "Неверный тип файла. Поддерживаются только JPEG и PNG",
                },
                500: {
                    "model": StorageErrorResponseSchema,
                    "description": "Ошибка при загрузке файла в хранилище",
                },
            },
        )
        @inject
        async def upload_avatar(
            profile_service: FromDishka[ProfileService],
            file: UploadFile = File(
                ...,
                description="Файл аватара",
                content_type=["image/jpeg", "image/png"],
                max_size=2_000_000,  # 2MB
            ),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AvatarResponseSchema:
            """
            ## 📤 Загрузка аватара пользователя

            Загружает новое изображение профиля для текущего пользователя

            ### Args:
            * **file**: Файл изображения (JPEG/PNG, до 2MB)

            ### Returns:
            * **AvatarResponseSchema**: URL-адрес загруженного аватара
            """
            return await profile_service.update_avatar(current_user, file)

        @self.router.delete(
            path="/avatar",
            response_model=AvatarResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                404: {
                    "model": ProfileNotFoundResponseSchema,
                    "description": "Профиль не найден",
                },
                500: {
                    "model": StorageErrorResponseSchema,
                    "description": "Ошибка при удалении файла из хранилища",
                },
            },
        )
        @inject
        async def delete_avatar(
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AvatarResponseSchema:
            """
            ## 🗑️ Удаление аватара пользователя

            Удаляет текущий аватар пользователя и возвращает к стандартному изображению

            ### Returns:
                * **AvatarResponseSchema**: Информация о результате операции удаления аватара
            """
            return await profile_service.delete_avatar(current_user)

        @self.router.get(
            path="/generate/username",
            response_model=UsernameResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
            },
        )
        @inject
        async def generate_username(
            profile_service: FromDishka[ProfileService],
            theme: UsernameTheme = Query(UsernameTheme.RANDOM, description="Тема для генерации имени"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UsernameResponseSchema:
            """
            ## 🔄 Генерация имени пользователя

            Генерирует случайное уникальное имя пользователя

            ### Returns:
                * **UsernameResponse**: Сгенерированное имя пользователя
            """
            username = await profile_service.generate_username()
            return UsernameResponseSchema(username=username)

        @self.router.get(
            path="/generate/password",
            response_model=PasswordResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
            },
        )
        @inject
        async def generate_password(
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> PasswordResponseSchema:
            """
            ## 🔐 Генерация надежного пароля

            Генерирует случайный надежный пароль, соответствующий требованиям безопасности

            ### Returns:
            * **PasswordResponseSchema**: Сгенерированный пароль
            """
            password = await profile_service.generate_password()
            return PasswordResponseSchema(password=password)
