from dishka.integrations.fastapi import FromDishka, inject

from app.routes.base import BaseRouter
from app.schemas import UserStatusResponseSchema
from app.services.v1.users.service import UserService

class UserRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="users", tags=["Users"])

    def configure(self):
        @self.router.get("/{user_id}/status", response_model=UserStatusResponseSchema)
        @inject
        async def authenticate(
            user_service: FromDishka[UserService],
            user_id: int,
        ) -> UserStatusResponseSchema:
            """
            Получение статуса пользователя.
            **Args**:
                user_id (int): Идентификатор пользователя.

            **Returns**:
                UserStatusResponseSchema: Статус пользователя.
            """
            return await user_service.get_user_status(user_id)