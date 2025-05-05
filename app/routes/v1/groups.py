from typing import Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Path, Query

from app.core.security.auth import get_current_user
from app.core.security.access import require_permission
from app.models.v1.access import PermissionType, ResourceType
from app.routes.base import BaseRouter
from app.schemas import (CurrentUserSchema, Page, PaginationParams)
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.schemas.v1.users.exceptions import ForbiddenResponseSchema
from app.schemas.v1.groups.exceptions import (GroupNotFoundResponseSchema,
                                             UserAlreadyInGroupResponseSchema,
                                             UserNotInGroupResponseSchema)
from app.schemas.v1.groups.requests import (AddUserToGroupRequestSchema,
                                           RemoveUserFromGroupRequestSchema,
                                           UserGroupCreateRequestSchema,
                                           UserGroupUpdateRequestSchema)
from app.schemas.v1.groups.responses import (UserGroupCreateResponseSchema,
                                            UserGroupDeleteResponseSchema,
                                            UserGroupListResponseSchema,
                                            UserGroupMemberResponseSchema,
                                            UserGroupMembersResponseSchema,
                                            UserGroupResponseSchema,
                                            UserGroupUpdateResponseSchema)
from app.services.v1.groups.service import GroupService


class GroupRouter(BaseRouter):
    """
    Класс для настройки маршрутов групп пользователей.

    Этот класс предоставляет маршруты для управления группами пользователей,
    такие как создание групп, получение списка групп, обновление групп,
    удаление групп, а также управление членством пользователей в группах.
    """

    def __init__(self):
        super().__init__(prefix="groups", tags=["Groups"])

    def configure(self):
        @self.router.post(
            path="",
            response_model=UserGroupCreateResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
            },
        )
        @inject
        async def create_group(
            group_service: FromDishka[GroupService],
            group_data: UserGroupCreateRequestSchema,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupCreateResponseSchema:
            """
            ## 📝 Создание новой группы пользователей

            Создает новую группу пользователей с указанными параметрами.

            ### Args:
            * **name**: Название группы
            * **description**: Описание группы (опционально)
            * **workspace_id**: ID рабочего пространства (опционально)

            ### Returns:
            * Созданная группа пользователей
            """
            return await group_service.create_group(group_data, current_user)

        @self.router.get(
            path="",
            response_model=UserGroupListResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
            },
        )
        @inject
        async def get_groups(
            group_service: FromDishka[GroupService],
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: Optional[str] = Query(
                "name",
                description="Поле для сортировки групп"
            ),
            sort_desc: bool = Query(False, description="Сортировка по убыванию"),
            workspace_id: Optional[int] = Query(
                None, description="ID рабочего пространства для фильтрации"
            ),
            name: Optional[str] = Query(
                None, description="Поиск по названию группы"
            ),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupListResponseSchema:
            """
            ## 📋 Получение списка групп пользователей

            Возвращает список групп пользователей с пагинацией, фильтрацией и поиском

            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки
            * **sort_desc**: Сортировка по убыванию
            * **workspace_id**: ID рабочего пространства для фильтрации
            * **name**: Поиск по названию группы

            ### Returns:
            * Страница с группами пользователей
            """
            pagination = PaginationParams(
                skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
            )

            return await group_service.get_groups(
                pagination=pagination,
                workspace_id=workspace_id,
                name=name,
                current_user=current_user,
            )

        @self.router.get(
            path="/{group_id}",
            response_model=UserGroupResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": GroupNotFoundResponseSchema,
                    "description": "Группа не найдена",
                },
            },
        )
        @inject
        async def get_group(
            group_service: FromDishka[GroupService],
            group_id: int = Path(..., description="Идентификатор группы"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupResponseSchema:
            """
            ## 👥 Получение информации о группе

            Возвращает подробную информацию о группе пользователей

            ### Args:
            * **group_id**: Идентификатор группы

            ### Returns:
            * Данные группы пользователей
            """
            return await group_service.get_group(group_id, current_user)

        @self.router.put(
            path="/{group_id}",
            response_model=UserGroupUpdateResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": GroupNotFoundResponseSchema,
                    "description": "Группа не найдена",
                },
            },
        )
        @inject
        async def update_group(
            group_service: FromDishka[GroupService],
            group_data: UserGroupUpdateRequestSchema,
            group_id: int = Path(..., description="Идентификатор группы"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupUpdateResponseSchema:
            """
            ## ✏️ Обновление группы пользователей

            Обновляет данные группы пользователей

            ### Args:
            * **group_id**: Идентификатор группы
            * **name**: Новое название группы (опционально)
            * **description**: Новое описание группы (опционально)
            * **is_active**: Новый статус активности (опционально)

            ### Returns:
            * Обновленные данные группы
            """
            return await group_service.update_group(group_id, group_data, current_user)

        @self.router.delete(
            path="/{group_id}",
            response_model=UserGroupDeleteResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": GroupNotFoundResponseSchema,
                    "description": "Группа не найдена",
                },
            },
        )
        @inject
        async def delete_group(
            group_service: FromDishka[GroupService],
            group_id: int = Path(..., description="Идентификатор группы"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupDeleteResponseSchema:
            """
            ## 🗑️ Удаление группы пользователей

            Удаляет группу пользователей с указанным идентификатором

            ### Args:
            * **group_id**: Идентификатор группы

            ### Returns:
            * Статус операции удаления
            """
            return await group_service.delete_group(group_id, current_user)

        @self.router.get(
            path="/{group_id}/members",
            response_model=UserGroupMembersResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": GroupNotFoundResponseSchema,
                    "description": "Группа не найдена",
                },
            },
        )
        @inject
        async def get_group_members(
            group_service: FromDishka[GroupService],
            group_id: int = Path(..., description="Идентификатор группы"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupMembersResponseSchema:
            """
            ## 👥 Получение списка участников группы

            Возвращает список пользователей, входящих в группу

            ### Args:
            * **group_id**: Идентификатор группы

            ### Returns:
            * Список участников группы
            """
            return await group_service.get_group_members(group_id, current_user)

        @self.router.post(
            path="/{group_id}/members",
            response_model=UserGroupMemberResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": GroupNotFoundResponseSchema,
                    "description": "Группа не найдена",
                },
                400: {
                    "model": UserAlreadyInGroupResponseSchema,
                    "description": "Пользователь уже состоит в группе",
                },
            },
        )
        @inject
        async def add_user_to_group(
            group_service: FromDishka[GroupService],
            request: AddUserToGroupRequestSchema,
            group_id: int = Path(..., description="Идентификатор группы"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupMemberResponseSchema:
            """
            ## ➕ Добавление пользователя в группу

            Добавляет пользователя в указанную группу

            ### Args:
            * **group_id**: Идентификатор группы
            * **user_id**: Идентификатор пользователя

            ### Returns:
            * Данные о членстве пользователя в группе
            """
            return await group_service.add_user_to_group(group_id, request, current_user)

        @self.router.delete(
            path="/{group_id}/members",
            response_model=UserGroupDeleteResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": GroupNotFoundResponseSchema,
                    "description": "Группа не найдена",
                },
                400: {
                    "model": UserNotInGroupResponseSchema,
                    "description": "Пользователь не состоит в группе",
                },
            },
        )
        @inject
        async def remove_user_from_group(
            group_service: FromDishka[GroupService],
            request: RemoveUserFromGroupRequestSchema,
            group_id: int = Path(..., description="Идентификатор группы"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupDeleteResponseSchema:
            """
            ## ➖ Удаление пользователя из группы

            Удаляет пользователя из указанной группы

            ### Args:
            * **group_id**: Идентификатор группы
            * **user_id**: Идентификатор пользователя

            ### Returns:
            * Статус операции удаления
            """
            return await group_service.remove_user_from_group(group_id, request, current_user)

        @self.router.get(
            path="/users/{user_id}",
            response_model=UserGroupListResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
            },
        )
        @inject
        async def get_user_groups(
            group_service: FromDishka[GroupService],
            user_id: int = Path(..., description="Идентификатор пользователя"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserGroupListResponseSchema:
            """
            ## 📋 Получение групп пользователя

            Возвращает список групп, в которых состоит пользователь

            ### Args:
            * **user_id**: Идентификатор пользователя
            ### Returns:
            * Список групп пользователя
            """
            groups = await group_service.get_user_groups(user_id, current_user)

            # Формируем ответ с пагинацией
            page = Page(
                items=groups,
                total=len(groups),
                page=1,
                size=len(groups),
            )

            return UserGroupListResponseSchema(data=page)