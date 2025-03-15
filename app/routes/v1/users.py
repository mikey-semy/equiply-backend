from fastapi import Query, Depends, Path, Body
from dishka.integrations.fastapi import FromDishka, inject

from app.routes.base import BaseRouter
from app.schemas import (
    Page, PaginationParams,
    UserRole, UserSchema, UserStatusResponseSchema,
    CurrentUserSchema, UserActiveUpdateResponseSchema,
    UserRoleUpdateResponseSchema, UserDeleteResponseSchema,
    ToggleUserActiveSchema, AssignUserRoleSchema
)
from app.schemas.v1.users.exceptions import (
    UserNotFoundResponseSchema,
    ForbiddenResponseSchema
)
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.services.v1.users.service import UserService
from app.core.security.auth import get_current_user

class UserRouter(BaseRouter):
    """
    Класс для настройки маршрутов пользователей.

    Этот класс предоставляет маршруты для управления пользователями,
    такие как получение списка пользователей, получение статуса пользователя,
    изменение статуса пользователя, назначение роли пользователю,
    обновление роли пользователя и удаление пользователя.
    """
    def __init__(self):
        super().__init__(prefix="users", tags=["Users"])

    def configure(self):
        @self.router.get(
            path="/{user_id}/status",
            response_model=UserStatusResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует"
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден"
                }
            }
        )
        @inject
        async def get_user_status(
            user_service: FromDishka[UserService],
            user_id: int = Path(..., description="Идентификатор пользователя"),
            _current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> UserStatusResponseSchema:
            """
            ## 👤 Получение статуса пользователя

            Возвращает информацию о статусе пользователя (онлайн/офлайн, последняя активность)

            ### Parameters:
            * **user_id**: Идентификатор пользователя

            ### Returns:
            * Статус пользователя
            """
            return await user_service.get_user_status(user_id)

        @self.router.get(
            path="/",
            response_model=Page[UserSchema],
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует"
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции"
                }
            })
        @inject
        async def get_users(
            user_service: FromDishka[UserService],
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
            sort_by: str = Query("updated_at", description="Поле для сортировки"),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            role: UserRole = Query(None, description="Фильтрация по роли пользователя"),
            search: str = Query(None, description="Поиск по данным пользователя"),
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> Page[UserSchema]:
            """
            ## 📋 Получение списка пользователей

            Возвращает список пользователей с пагинацией, фильтрацией и поиском

            ### Parameters:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки
            * **sort_desc**: Сортировка по убыванию
            * **role**: Роль пользователя для фильтрации
            * **search**: Строка поиска по данным пользователя

            ### Returns:
            * Страница с пользователями
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
                current_user=current_user
            )
            return Page(
                items=users, total=total, page=pagination.page, size=pagination.limit
            )

        @self.router.post(
            path="/active",
            response_model=UserActiveUpdateResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует"
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции"
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден"
                }
            }
        )
        @inject
        async def toggle_active(
            user_service: FromDishka[UserService],
            request: ToggleUserActiveSchema,
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> UserActiveUpdateResponseSchema:
            """
            ## 🔄 Активация/деактивация пользователя

            Изменяет статус активности пользователя (блокировка/разблокировка)
            Доступно только для администраторов и модераторов.

            ### Parameters:
            * **user_id**: Идентификатор пользователя
            * **is_active**: Статус активности (true - активен, false - заблокирован)

            ### Returns:
            * Обновленные данные пользователя
            """
            return await user_service.toggle_active(request.user_id, request.is_active, current_user)

        @self.router.post(
            path="/role",
            response_model=UserRoleUpdateResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует"
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции"
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден"
                }
            })
        @inject
        async def assign_role_user(
            user_service: FromDishka[UserService],
            request: AssignUserRoleSchema,
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> UserRoleUpdateResponseSchema:
            """
            ## 👑 Присвоение роли пользователю

            Изменяет роль пользователя в системе

            ### Parameters:
            * **user_id**: Идентификатор пользователя
            * **role**: Новая роль пользователя

            ### Returns:
            * Обновленные данные пользователя
            """
            return await user_service.assign_role(request.user_id, request.role, current_user)

        @self.router.delete(
            path="/{user_id}",
            response_model=UserDeleteResponseSchema,
            responses={
                401: {
                     "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует"
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции"
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден"
                }
            }
        )
        @inject
        async def delete_user(
            user_service: FromDishka[UserService],
            user_id: int = Path(..., description="Идентификатор пользователя"),
            current_user: CurrentUserSchema = Depends(get_current_user)
        ) -> UserDeleteResponseSchema:
            """
            ## 🗑️ Удаление пользователя

            Удаляет пользователя с указанным идентификатором

            ### Parameters:
            * **user_id**: Идентификатор пользователя (path parameter)

            ### Returns:
            * Статус операции удаления
            """
            return await user_service.delete_user(user_id, current_user)