from fastapi import Depends
from dishka.integrations.fastapi import FromDishka, inject
from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas import CurrentUserSchema, PasswordFormSchema, ProfileSchema, ProfileResponseSchema, PasswordUpdateResponseSchema
from app.services.v1.profile.service import ProfileService

class ProfileRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="profile", tags=["Profile"])

    def configure(self):
        @self.router.get("", response_model=ProfileResponseSchema)
        @inject
        async def get_profile(
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> ProfileResponseSchema:
            """
            ## Получение профиля пользователя.
            
            ### Returns:
            * **ProfileResponseSchema**: Полная информация о профиле пользователя
            """
            return await profile_service.get_profile(current_user)
        
        @self.router.put("", response_model=ProfileResponseSchema)
        @inject
        async def update_profile(
            profile_data: ProfileSchema,
            profile_service: FromDishka[ProfileService],
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> ProfileResponseSchema:
            """
            ## Обновление профиля пользователя.
            
            ### Returns:
            * **ProfileResponseSchema**: Полная информация о профиле пользователя
            """
            return await profile_service.update_profile(current_user, profile_data)
        
        @self.router.put("/password", response_model=PasswordUpdateResponseSchema)
        @inject
        async def update_password(
            profile_service: FromDishka[ProfileService],
            password_data: PasswordFormSchema,
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> PasswordUpdateResponseSchema:
            """
            ## 🔄 Обновление пароля пользователя.
    
            Требует текущий пароль для безопасности и проверяет, 
            что новый пароль и подтверждение совпадают.
            """
            return await profile_service.update_password(current_user, password_data)