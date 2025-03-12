from fastapi import Query, Depends
from dishka.integrations.fastapi import FromDishka, inject

from app.routes.base import BaseRouter
from app.schemas import (
    Page, PaginationParams,
    UserRole, UserSchema, UserStatusResponseSchema,
    UserUpdateSchema, CurrentUserSchema
)
from app.services.v1.users.service import UserService
from app.core.security.auth import get_current_user

class UserRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="users", tags=["Users"])

    def configure(self):
        @self.router.get("/{user_id}/status", response_model=UserStatusResponseSchema)
        @inject
        async def get_user_status(
            user_service: FromDishka[UserService],
            user_id: int,
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> UserStatusResponseSchema:
            """
            **Получение статуса пользователя**

            **Args**:
                user_id (int): Идентификатор пользователя.

            **Returns**:
                UserStatusResponseSchema: Статус пользователя.
            """
            return await user_service.get_user_status(user_id)

        @self.router.get("/", response_model=Page[UserSchema])
        @inject
        async def get_users(
            user_service: FromDishka[UserService],
            pagination: FromDishka[PaginationParams],
            role: UserRole = Query(None, description="Фильтрация по роли пользователя"),
            search: str = Query(None, description="Поиск по данным пользователя"),
        ) -> Page[UserSchema]:
            """
            **Получение всех пользователей с пагинацией, фильтрацией и поиском.**

            **Args**:
                - pagination (PaginationParams): Параметры пагинации.
                - role (UserRole): Статус отзыва для фильтрации.
                - search (str): Строка поиска по тексту отзыва.

            **Returns**:
                - Page[UserSchema]: Страница с пользователями.


            """
            users, total = await user_service.get_users(
                pagination=pagination,
                role=role,
                search=search,
            )
            return Page(
                items=users, total=total, page=pagination.page, size=pagination.limit
            )

        @self.router.post("/active", response_model=UserUpdateSchema)
        @inject
        async def toggle_active(
            user_service: FromDishka[UserService],
            user_id: int,
            is_active: bool,
        ) -> UserUpdateSchema:
            """
            Активация/деактивация пользователя.

            Args:
                user_id (int): Идентификатор пользователя
                is_active (bool): Статус активности

            Returns:
                UserUpdateSchema: Обновленные данные пользователя
            """
            return await user_service.toggle_active(user_id, is_active)

        @self.router.post("/role", response_model=UserUpdateSchema)
        @inject
        async def create_user(
            user_service: FromDishka[UserService],
            user_id: int,
            role: UserRole,
        ) -> UserUpdateSchema:
            """
            Присвоение роли пользователю.

            **Args**:
                user_id (int): Идентификатор пользователя.
                role (UserRole): Роль для присвоения.

            **Returns**:
                UserUpdateSchema: Схема обновления данных пользователя.
            """
            return await user_service.assign_role(user_id, role)
