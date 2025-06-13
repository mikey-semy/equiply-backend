"""Маршруты для работы с рабочими пространствами."""
import uuid
from typing import Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Query

from app.core.security.access import require_permission
from app.core.security.auth import get_current_user
from app.models.v1.access import PermissionType, ResourceType
from app.models.v1.workspaces import WorkspaceRole
from app.routes.base import BaseRouter
from app.schemas import (AddWorkspaceMemberSchema, CreateWorkspaceSchema,
                         CurrentUserSchema, Page, PaginationParams,
                         UpdateWorkspaceMemberRoleSchema,
                         UpdateWorkspaceSchema,
                         WorkspaceAccessDeniedResponseSchema,
                         WorkspaceCreateResponseSchema,
                         WorkspaceDeleteResponseSchema,
                         WorkspaceDetailResponseSchema,
                         WorkspaceListResponseSchema,
                         WorkspaceMemberAddResponseSchema,
                         WorkspaceMemberListResponseSchema,
                         WorkspaceMemberRemoveResponseSchema,
                         WorkspaceMemberSortFields,
                         WorkspaceMemberUpdateResponseSchema,
                         WorkspaceNotFoundResponseSchema,
                         WorkspaceResponseSchema, WorkspaceSortFields,
                         WorkspaceUpdateResponseSchema)
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.services.v1.workspaces.service import WorkspaceService


class WorkspaceRouter(BaseRouter):
    """Маршруты для работы с рабочими пространствами."""

    def __init__(self):
        super().__init__(prefix="workspaces", tags=["Workspaces"])

    def configure(self):
        """Настройка маршрутов для рабочих пространств."""

        @self.router.post(path="", response_model=WorkspaceCreateResponseSchema)
        @inject
        async def create_workspace(
            workspace_data: CreateWorkspaceSchema,
            workspace_service: FromDishka[WorkspaceService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceCreateResponseSchema:
            """
            ## ➕ Создание рабочего пространства

            Создает новое рабочее пространство с текущим пользователем в качестве владельца.

            ### Args:
            * **name**: Название рабочего пространства
            * **description**: Описание рабочего пространства (опционально)
            * **is_public**: Флаг публичности (по умолчанию false)

            ### Returns:
            * **data**: Данные созданного рабочего пространства
            * **message**: Сообщение о результате операции

            TODO:
            - Название рабочего пространства (Демо, ЛПЦ-1, Обслуживание оборудования)
            - Префикс ID задач проекта (DEM, LPС, OBS)
            - Участники проекта: поиск по имени, должности, отделу (Поиск с выделением совпадений)
            - Настройка ролей в проекте:

                Добавить роль или Копировать из другого проекта

                Стандартные роли:
                - Управляющий (OWNER, ADMIN, MODERATOR)
                    Полный доступ. Может менять структуру и пользователей проекта.
                    Настраивать права, создавать доски и колонки.
                - Сотрудник (EDITOR)
                    Доступ к задачам. Может работать с задачами,
                    но не менять структуру проекта (доски, колонки).
                - Наблюдатель (VIEWER)
                    Доступ к чатам. Может комментировать в чате,
                    ничего не меняя в задачах.

                Создание роли:
                - Название роли
                - Описание роли
                - Права доступа к выбранному объекту
                    - Проект
                        - Удаление проекта
                        - Изменение названия проекта
                        - Добавление доски
                    - Доски
                        - Удаление доски
                        - Изменение названия доски
                        - Отображение панели стикеров
                        - Изменение стикеров в доске
                        - Перемещение доски
                        - Добавление колонки
                        - Управление основными настройками доски
                    - Колонки
                        - Удаление колонки
                        - Изменение названия колонки
                        - Перемещение колонки (Запретить, Разрешить только внутри проекта, Разрешить)
                        - Добавление задачи
                    - Все задачи
                        - Просмотр задачи
                        - Изменение названия задачи
                        - Выполнение задач
                        - Назначение исполнителя
                            - Запретить,
                            - Разрешить назначать себя, если не назначено
                            - Разрешить назначать себя
                            - Разрешить менять с себя на другого
                            - Разрешить любые назначения
                        - Изменение подзадач и чеклистов
                            - Разрешить
                            - Разрешить отмечать выполненными
                            - Запретить
                        - Изменение стикеров и цвета в задаче
                        - Изменение быстрых ссылок в чате
                        - Перемещение задачи
                        - Изменение описания задачи
                        - Отправка сообщений в задаче
                        - Отправка файлов в чате
                        - Изменение списка “Получат уведомление”
                            - Запретить
                            - Разрешить добавлять себя
                            - Разрешить инзменение списка
                            - Архивирование задачи
                            - Связывание задач
                            - Удаление задачи
                        *Более сложные дальше:
                        - Задачи, созданные пользователем - Как у остальных задач
                        - Назначенные на пользователя задачи - Как у остальных задач
                        - Задачи, где пользователь добавлен в уведомления - Как у остальных задач
            - Таблица участников: Имя, Должность, Отдел, Роль в проекте
            """
            return await workspace_service.create_workspace(
                workspace_data, current_user
            )

        @self.router.get(
            path="",
            response_model=WorkspaceListResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            },
        )
        @inject
        async def get_workspaces(
            workspace_service: FromDishka[WorkspaceService],
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: Optional[str] = Query(
                WorkspaceSortFields.get_default().field,
                description=(
                    "Поле для сортировки рабочих пространств. "
                    f"Доступные значения: {', '.join(WorkspaceSortFields.get_field_values())}. "
                    f"По умолчанию: {WorkspaceSortFields.get_default().field} "
                    f"({WorkspaceSortFields.get_default().description})."
                ),
                enum=WorkspaceSortFields.get_field_values(),
            ),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            search: Optional[str] = Query(
                None, description="Поиск по данным рабочего пространства"
            ),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceListResponseSchema:
            """
            ## 📋 Получение списка рабочих пространств

            Возвращает список рабочих пространств, доступных текущему пользователю.

            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки
            * **sort_desc**: Сортировка по убыванию
            * **search**: Поисковый запрос (опционально)

            ### Returns:
            * Страница с рабочими пространствами
            """
            pagination = PaginationParams(
                skip=skip,
                limit=limit,
                sort_by=sort_by,
                sort_desc=sort_desc,
                entity_name="Workspace",
            )

            workspaces, total = await workspace_service.get_workspaces(
                current_user=current_user,
                pagination=pagination,
                search=search,
            )

            page = Page(
                items=workspaces,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return WorkspaceListResponseSchema(data=page)

        @self.router.get("/{workspace_id}", response_model=WorkspaceResponseSchema)
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.READ,
            resource_id_param="workspace_id"
        )
        @inject
        async def get_workspace(
            workspace_id: int,
            workspace_service: FromDishka[WorkspaceService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceResponseSchema:
            """
            ## 🔍 Получение рабочего пространства

            Возвращает информацию о рабочем пространстве по его ID.

            ### Args:
            * **workspace_id**: ID рабочего пространства

            ### Returns:
            * **data**: Данные рабочего пространства
            * **message**: Сообщение о результате операции
            """
            workspace_data = await workspace_service.get_workspace(
                workspace_id, current_user
            )
            return WorkspaceResponseSchema(data=workspace_data)

        @self.router.get(
            "/{workspace_id}/details", response_model=WorkspaceDetailResponseSchema
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.READ,
            resource_id_param="workspace_id"
        )
        @inject
        async def get_workspace_details(
            workspace_id: int,
            workspace_service: FromDishka[WorkspaceService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceDetailResponseSchema:
            """
            ## 📊 Получение детальной информации о рабочем пространстве

            Возвращает детальную информацию о рабочем пространстве, включая список участников,
            количество таблиц и списков.

            ### Args:
            * **workspace_id**: ID рабочего пространства

            ### Returns:
            * **data**: Детальные данные рабочего пространства
            * **message**: Сообщение о результате операции
            """
            workspace_detail_data = await workspace_service.get_workspace_details(
                workspace_id, current_user
            )
            return WorkspaceDetailResponseSchema(data=workspace_detail_data)

        @self.router.put(
            path="/{workspace_id}", response_model=WorkspaceUpdateResponseSchema
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.WRITE,
            resource_id_param="workspace_id"
        )
        @inject
        async def update_workspace(
            workspace_id: int,
            workspace_data: UpdateWorkspaceSchema,
            workspace_service: FromDishka[WorkspaceService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceUpdateResponseSchema:
            """
            ## ✏️ Обновление рабочего пространства

            Обновляет информацию о рабочем пространстве.

            ### Args:
            * **workspace_id**: ID рабочего пространства

            ### Тело запроса:
            * **name**: Новое название рабочего пространства (опционально)
            * **description**: Новое описание рабочего пространства (опционально)
            * **is_public**: Новый флаг публичности (опционально)

            ### Returns:
            * **data**: Данные обновленного рабочего пространства
            * **message**: Сообщение о результате операции
            """
            updated_workspace = await workspace_service.update_workspace(
                workspace_id, current_user, workspace_data
            )
            return WorkspaceUpdateResponseSchema(data=updated_workspace)

        @self.router.delete(
            "/{workspace_id}", response_model=WorkspaceDeleteResponseSchema
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.DELETE,
            resource_id_param="workspace_id"
        )
        @inject
        async def delete_workspace(
            workspace_id: int,
            workspace_service: FromDishka[WorkspaceService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceDeleteResponseSchema:
            """
            ## 🗑️ Удаление рабочего пространства

            Удаляет рабочее пространство. Только владелец может удалить рабочее пространство.

            ### Args:
            * **workspace_id**: ID рабочего пространства

            ### Returns:
            * **message**: Сообщение о результате операции
            """
            return await workspace_service.delete_workspace(workspace_id, current_user)

        @self.router.get(
            path="/{workspace_id}/members",
            response_model=WorkspaceMemberListResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": WorkspaceAccessDeniedResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": WorkspaceNotFoundResponseSchema,
                    "description": "Рабочее пространство не найдено",
                },
            },
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.READ,
            resource_id_param="workspace_id"
        )
        @inject
        async def get_workspace_members(
            workspace_service: FromDishka[WorkspaceService],
            workspace_id: int,
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: Optional[str] = Query(
                WorkspaceMemberSortFields.get_default().field,
                description=(
                    "Поле для сортировки участников. "
                    f"Доступные значения: {', '.join(WorkspaceMemberSortFields.get_field_values())}. "
                    f"По умолчанию: {WorkspaceMemberSortFields.get_default().field} "
                    f"({WorkspaceMemberSortFields.get_default().description})."
                ),
                enum=WorkspaceMemberSortFields.get_field_values(),
            ),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            role: Optional[WorkspaceRole] = Query(
                None, description="Фильтрация по роли участника"
            ),
            search: Optional[str] = Query(
                None, description="Поиск по данным рабочего пространства"
            ),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceMemberListResponseSchema:
            """
            ## 👥 Получение списка участников рабочего пространства

            Возвращает список участников рабочего пространства с пагинацией и сортировкой

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки
            * **sort_desc**: Сортировка по убыванию

            ### Returns:
            * Страница с участниками рабочего пространства
            """
            pagination = PaginationParams(
                skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
            )

            members, total = await workspace_service.get_workspace_members(
                workspace_id=workspace_id,
                pagination=pagination,
                role=role,
                search=search,
                current_user=current_user,
            )

            page = Page(
                items=members, total=total, page=pagination.page, size=pagination.limit
            )
            return WorkspaceMemberListResponseSchema(data=page)

        @self.router.post(
            "/{workspace_id}/members", response_model=WorkspaceMemberAddResponseSchema
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.MANAGE,
            resource_id_param="workspace_id"
        )
        @inject
        async def add_workspace_member(
            workspace_id: int,
            member_data: AddWorkspaceMemberSchema,
            workspace_service: FromDishka[WorkspaceService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceMemberAddResponseSchema:
            """
            ## ➕ Добавление участника в рабочее пространство

            Добавляет нового участника в рабочее пространство или обновляет роль существующего.

            ### Args:
            * **workspace_id**: ID рабочего пространства

            ### Тело запроса:
            * **user_id**: ID пользователя для добавления
            * **role**: Роль пользователя в рабочем пространстве (по умолчанию "viewer")

            ### Returns:
            * **data**: Данные добавленного участника
            * **message**: Сообщение о результате операции
            """
            return await workspace_service.add_workspace_member(
                workspace_id=workspace_id,
                user_id=member_data.user_id,
                role=member_data.role,
                current_user=current_user,
            )

        @self.router.put(
            "/{workspace_id}/members",
            response_model=WorkspaceMemberUpdateResponseSchema,
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.MANAGE,
            resource_id_param="workspace_id"
        )
        @inject
        async def update_workspace_member_role(
            workspace_id: int,
            member_data: UpdateWorkspaceMemberRoleSchema,
            workspace_service: FromDishka[WorkspaceService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceMemberUpdateResponseSchema:
            """
            ## 🔄 Обновление роли участника рабочего пространства

            Обновляет роль участника в рабочем пространстве.

            ### Args:
            * **workspace_id**: ID рабочего пространства

            ### Тело запроса:
            * **user_id**: ID пользователя
            * **role**: Новая роль пользователя

            ### Returns:
            * **data**: Данные участника с обновленной ролью
            * **message**: Сообщение о результате операции
            """
            return await workspace_service.update_workspace_member_role(
                workspace_id=workspace_id,
                user_id=member_data.user_id,
                role=member_data.role,
                current_user=current_user,
            )

        @self.router.delete(
            "/{workspace_id}/members/{user_id}",
            response_model=WorkspaceMemberRemoveResponseSchema,
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.DELETE,
            resource_id_param="workspace_id",
        )
        @inject
        async def remove_workspace_member(
            workspace_id: int,
            user_id: uuid.UUID,
            workspace_service: FromDishka[WorkspaceService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> WorkspaceMemberRemoveResponseSchema:
            """
            ## 🗑️ Удаление участника из рабочего пространства

            Удаляет участника из рабочего пространства. Пользователь может удалить сам себя
            или администратор/владелец может удалить любого участника, кроме владельца.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **user_id**: ID пользователя для удаления

            ### Returns:
            * **message**: Сообщение о результате операции
            """
            return await workspace_service.remove_workspace_member(
                workspace_id=workspace_id, user_id=user_id, current_user=current_user
            )
