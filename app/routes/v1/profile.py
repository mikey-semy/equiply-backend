from fastapi import Depends
from dishka.integrations.fastapi import FromDishka, inject
from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas import CurrentUserSchema, PasswordFormSchema, PasswordUpdateResponseSchema
from app.services.v1.profile.service import ProfileService

class ProfileRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="profile", tags=["Profile"])

    def configure(self):
        @self.router.put("/password", response_model=PasswordUpdateResponseSchema)
        @inject
        async def update_password(
            profile_service: FromDishka[ProfileService],
            password_data: PasswordFormSchema,
            _current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> PasswordUpdateResponseSchema:
            """
            🔄 Обновление пароля пользователя.

            Требует текущий пароль для безопасности и проверяет,
            что новый пароль и подтверждение совпадают.
            """
            return await profile_service.update_password(_current_user, password_data)