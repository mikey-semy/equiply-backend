from fastapi import Depends, File, UploadFile
from dishka.integrations.fastapi import FromDishka, inject
from app.core.security.auth import get_current_user
from app.core.exceptions import InvalidCredentialsError, ProfileNotFoundError
from app.routes.base import BaseRouter
from app.schemas import ErrorResponseSchema, CurrentUserSchema, PasswordFormSchema, ProfileUpdateSchema, ProfileResponseSchema, PasswordUpdateResponseSchema, AvatarResponseSchema
from app.services.v1.profile.service import ProfileService



class ProfileRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="profile", tags=["Profile"])

    def configure(self):
        @self.router.get(
            path="",
            response_model=ProfileResponseSchema,
            responses=self.create_error_responses(
                InvalidCredentialsError,  # 401
                ProfileNotFoundError      # 404
            )
        )
        @inject
        async def get_profile(
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user)
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
                    "model": ErrorResponseSchema,
                    "description": "Ошибка авторизации",
                    "content": {
                        "application/json": {
                            "example": {
                                "success": False,
                                "message": None,
                                "data": None,
                                "error": {
                                    "detail": "Not authenticated",
                                    "error_type": "http_error",
                                    "status_code": 401,
                                    "timestamp": "2025-03-13T10:58:45.254662+03:00",
                                    "request_id": "03441d78-6d5a-490d-a355-1c7452a876e9",
                                    "extra": None
                                }
                            }
                        }
                    }
                },
            }
        )
        @inject
        async def update_profile(
            profile_data: ProfileUpdateSchema,
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> ProfileResponseSchema:
            """
            ## ✏️ Обновление профиля пользователя

            Изменяет основные данные профиля текущего пользователя

            ### Parameters:
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
                401: {
                    "model": ErrorResponseSchema,
                    "description": "Текущий пароль неверен",

                },
                404: {
                    "model": ErrorResponseSchema,
                    "description": "Пользователь не найден",
                }
            }
        )
        @inject
        async def update_password(
            profile_service: FromDishka[ProfileService],
            password_data: PasswordFormSchema,
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> PasswordUpdateResponseSchema:
            """
            ## 🔄 Обновление пароля пользователя

            Изменяет пароль текущего пользователя

            ### Parameters:
            * **old_password**: Текущий пароль
            * **new_password**: Новый пароль
            * **confirm_password**: Подтверждение нового пароля

            ### Returns:
            * Статус операции изменения пароля
            """
            return await profile_service.update_password(current_user, password_data)

        @self.router.get("/avatar", response_model=AvatarResponseSchema)
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

        @self.router.post("/avatar", response_model=AvatarResponseSchema)
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

            ### Parameters:
            * **file**: Файл изображения (JPEG/PNG, до 2MB)

            ### Returns:
            * **AvatarResponseSchema**: URL-адрес загруженного аватара
            """
            return await profile_service.update_avatar(current_user, file)
