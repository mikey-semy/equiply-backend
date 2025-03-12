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
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
            sort_by: str = Query("updated_at", description="Поле для сортировки"),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            role: UserRole = Query(None, description="Фильтрация по роли пользователя"),
            search: str = Query(None, description="Поиск по данным пользователя"),
        ) -> Page[UserSchema]:
            """
            **Получение всех пользователей с пагинацией, фильтрацией и поиском.**

            **Args**:
                - skip (int): Количество пропускаемых элементов.
                - limit (int): Количество элементов на странице (от 1 до 100).
                - sort_by (str): Поле для сортировки.
                - sort_desc (bool): Сортировка по убыванию.
                - role (UserRole): Роль пользователя для фильтрации.
                - search (str): Строка поиска по данным пользователя.

            **Returns**:
                - Page[UserSchema]: Страница с пользователями.


            """
            pagination = PaginationParams(
                skip=skip,
                limit=limit,
                sort_by=sort_by,
                sort_desc=sort_desc
            )

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
