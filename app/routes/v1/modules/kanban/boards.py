"""Маршруты для работы с канбан-досками."""

from typing import Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Path, Query

from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.schemas.v1.modules.kanban.exceptions import (
    KanbanAccessDeniedResponseSchema, KanbanBoardNotFoundResponseSchema)
from app.schemas.v1.modules.kanban.requests import (
    CreateKanbanBoardSchema, UpdateKanbanBoardSchema,
    UpdateKanbanBoardSettingsSchema)
from app.schemas.v1.modules.kanban.responses import (
    KanbanBoardCreateResponseSchema, KanbanBoardDeleteResponseSchema,
    KanbanBoardDetailResponseSchema, KanbanBoardListResponseSchema,
    KanbanBoardResponseSchema, KanbanBoardSettingsResponseSchema,
    KanbanBoardSettingsUpdateResponseSchema, KanbanBoardUpdateResponseSchema,
    KanbanDefaultSettingsResponseSchema)
from app.schemas.v1.pagination import Page, PaginationParams
from app.schemas.v1.users import CurrentUserSchema
from app.schemas.v1.workspaces import (WorkspaceAccessDeniedResponseSchema,
                                       WorkspaceNotFoundResponseSchema)
from app.services.v1.modules.kanban.service import KanbanService


class KanbanBoardRouter(BaseRouter):
    """Маршруты для работы с канбан-досками."""

    def __init__(self):
        super().__init__(prefix="workspaces/{workspace_id}/kanban", tags=["Kanban"])

    def configure(self):
        """Настройка маршрутов для канбан-досок."""

        @self.router.post(
            path="/boards",
            response_model=KanbanBoardCreateResponseSchema,
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
        @inject
        async def create_kanban_board(
            workspace_id: int,
            board_data: CreateKanbanBoardSchema,
            kanban_service: FromDishka[KanbanService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanBoardCreateResponseSchema:
            """
            ## ➕ Создание канбан-доски

            Создает новую канбан-доску в рабочем пространстве.

            ### Args:
            * **workspace_id**: ID рабочего пространства

            ### Тело запроса:
            * **name**: Название канбан-доски
            * **description**: Описание канбан-доски (опционально)
            * **display_settings**: Настройки отображения доски (опционально)
            * **template_id**: ID шаблона модуля (опционально)

            ### Returns:
            * **data**: Данные созданной канбан-доски
            * **message**: Сообщение о результате операции

            ### Операции с доской хотелось бы реализовать:
            - Переименовать (PUT /boards/{board_id}/name)
            - Переместить (PUT /boards/{board_id}/workspace)
            - Дублировать (POST /boards/{board_id}/duplicate)
            - Доступ по ссылке (GET /boards/{board_id}/link)
            - Настройки доски (GET /boards/{board_id}/settings)
            - Удалить (DELETE /boards/{board_id}) - реализовано delete_kanban_board()
            """
            return await kanban_service.create_board(
                workspace_id=workspace_id,
                board_data=board_data,
                current_user=current_user,
            )

        @self.router.get(
            path="/boards",
            response_model=KanbanBoardListResponseSchema,
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
        @inject
        async def get_kanban_boards(
            workspace_id: int,
            kanban_service: FromDishka[KanbanService],
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: str = Query("updated_at", description="Поле для сортировки"),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            search: Optional[str] = Query(
                None, description="Поиск по названию канбан-доски"
            ),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanBoardListResponseSchema:
            """
            ## 📋 Получение списка канбан-досок

            Возвращает список канбан-досок в рабочем пространстве с пагинацией и поиском.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки
            * **sort_desc**: Сортировка по убыванию
            * **search**: Поисковый запрос (опционально)

            ### Returns:
            * Страница с канбан-досками
            """
            pagination = PaginationParams(
                skip=skip,
                limit=limit,
                sort_by=sort_by,
                sort_desc=sort_desc,
                entity_name="KanbanBoard",
            )

            boards, total = await kanban_service.get_boards(
                workspace_id=workspace_id,
                current_user=current_user,
                pagination=pagination,
                search=search,
            )

            page = Page(
                items=boards,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return KanbanBoardListResponseSchema(data=page)

        @self.router.get(
            path="/boards/{board_id}",
            response_model=KanbanBoardResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": KanbanAccessDeniedResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": KanbanBoardNotFoundResponseSchema,
                    "description": "Канбан-доска не найдена",
                },
            },
        )
        @inject
        async def get_kanban_board(
            workspace_id: int,
            board_id: int = Path(..., description="ID канбан-доски"),
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanBoardResponseSchema:
            """
            ## 🔍 Получение канбан-доски

            Возвращает информацию о канбан-доске по её ID.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **board_id**: ID канбан-доски

            ### Returns:
            * **data**: Данные канбан-доски
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.get_board(
                board_id=board_id,
                current_user=current_user,
            )

        @self.router.get(
            path="/boards/{board_id}/details",
            response_model=KanbanBoardDetailResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": KanbanAccessDeniedResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": KanbanBoardNotFoundResponseSchema,
                    "description": "Канбан-доска не найдена",
                },
            },
        )
        @inject
        async def get_kanban_board_details(
            workspace_id: int,
            board_id: int = Path(..., description="ID канбан-доски"),
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanBoardDetailResponseSchema:
            """
            ## 📊 Получение детальной информации о канбан-доске

            Возвращает детальную информацию о канбан-доске, включая колонки и карточки.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **board_id**: ID канбан-доски

            ### Returns:
            * **data**: Детальные данные канбан-доски, включая колонки и карточки
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.get_board_details(
                board_id=board_id,
                current_user=current_user,
            )

        @self.router.put(
            path="/boards/{board_id}",
            response_model=KanbanBoardUpdateResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": KanbanAccessDeniedResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": KanbanBoardNotFoundResponseSchema,
                    "description": "Канбан-доска не найдена",
                },
            },
        )
        @inject
        async def update_kanban_board(
            workspace_id: int,
            board_id: int,
            board_data: UpdateKanbanBoardSchema,
            kanban_service: FromDishka[KanbanService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanBoardUpdateResponseSchema:
            """
            ## ✏️ Обновление канбан-доски

            Обновляет информацию о канбан-доске.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **board_id**: ID канбан-доски

            ### Тело запроса:
            * **name**: Новое название канбан-доски (опционально)
            * **description**: Новое описание канбан-доски (опционально)
            * **display_settings**: Новые настройки отображения доски (опционально)

            ### Returns:
            * **data**: Данные обновленной канбан-доски
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.update_board(
                board_id=board_id,
                board_data=board_data,
                current_user=current_user,
            )

        @self.router.delete(
            path="/boards/{board_id}",
            response_model=KanbanBoardDeleteResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": KanbanAccessDeniedResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
                404: {
                    "model": KanbanBoardNotFoundResponseSchema,
                    "description": "Канбан-доска не найдена",
                },
            },
        )
        @inject
        async def delete_kanban_board(
            workspace_id: int,
            board_id: int = Path(..., description="ID канбан-доски"),
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanBoardDeleteResponseSchema:
            """
            ## 🗑️ Удаление канбан-доски

            Удаляет канбан-доску и все связанные с ней данные.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **board_id**: ID канбан-доски

            ### Returns:
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.delete_board(
                board_id=board_id,
                current_user=current_user,
            )

        # @self.router.get(
        #     path="/boards/{board_id}/settings",
        #     response_model=KanbanBoardSettingsResponseSchema,
        #     responses={
        #         401: {"model": TokenMissingResponseSchema, "description": "Токен отсутствует"},
        #         403: {"model": KanbanAccessDeniedResponseSchema, "description": "Недостаточно прав для выполнения операции"},
        #         404: {"model": KanbanBoardNotFoundResponseSchema, "description": "Канбан-доска не найдена"},
        #     },
        # )
        # @inject
        # async def get_kanban_board_settings(
        #     workspace_id: int,
        #     board_id: int = Path(..., description="ID канбан-доски"),
        #     kanban_service: FromDishka[KanbanService] = None,
        #     current_user: CurrentUserSchema = Depends(get_current_user),
        # ) -> KanbanBoardSettingsResponseSchema:
        #     """
        #     ## ⚙️ Получение настроек канбан-доски

        #     Возвращает настройки отображения и другие конфигурации канбан-доски.

        #     ### Args:
        #         * **workspace_id**: ID рабочего пространства
        #         * **board_id**: ID канбан-доски

        #     ### Returns:
        #         * **data**: Объект с настройками канбан-доски
        #         * **message**: Сообщение о результате операции
        #     """
        #     return await kanban_service.get_board_settings(
        #         board_id=board_id,
        #         current_user=current_user,
        #     )

        # @self.router.put(
        #     path="/boards/{board_id}/settings",
        #     response_model=KanbanBoardSettingsUpdateResponseSchema,
        #     responses={
        #         401: {"model": TokenMissingResponseSchema, "description": "Токен отсутствует"},
        #         403: {"model": KanbanAccessDeniedResponseSchema, "description": "Недостаточно прав для выполнения операции"},
        #         404: {"model": KanbanBoardNotFoundResponseSchema, "description": "Канбан-доска не найдена"},
        #     },
        # )
        # @inject
        # async def update_kanban_board_settings(
        #     workspace_id: int,
        #     board_id: int = Path(..., description="ID канбан-доски"),
        #     settings_data: UpdateKanbanBoardSettingsSchema = Body(..., description="Настройки канбан-доски"),
        #     kanban_service: FromDishka[KanbanService] = None,
        #     current_user: CurrentUserSchema = Depends(get_current_user),
        # ) -> KanbanBoardSettingsUpdateResponseSchema:
        #     """
        #     ## 🔧 Обновление настроек канбан-доски

        #     Обновляет настройки отображения и другие конфигурации канбан-доски.

        #     ### Args:
        #         * **workspace_id**: ID рабочего пространства
        #         * **board_id**: ID канбан-доски
        #         * **settings_data**: Настройки канбан-доски

        #     ### Тело запроса:
        #         * **display_settings**: Настройки отображения доски
        #         * **automation_settings**: Настройки автоматизации (опционально)
        #         * **notification_settings**: Настройки уведомлений (опционально)
        #         * **access_settings**: Настройки доступа (опционально)

        #     ### Returns:
        #         * **data**: Обновленные настройки канбан-доски
        #         * **message**: Сообщение о результате операции
        #     """
        #     return await kanban_service.update_board_settings(
        #         board_id=board_id,
        #         settings_data=settings_data,
        #         current_user=current_user,
        #     )

        # @self.router.get(
        #     path="/settings/defaults",
        #     response_model=KanbanDefaultSettingsResponseSchema,
        #     responses={
        #         401: {"model": TokenMissingResponseSchema, "description": "Токен отсутствует"},
        #         403: {"model": WorkspaceAccessDeniedResponseSchema, "description": "Недостаточно прав для выполнения операции"},
        #     },
        # )
        # @inject
        # async def get_default_kanban_settings(
        #     workspace_id: int,
        #     kanban_service: FromDishka[KanbanService] = None,
        #     current_user: CurrentUserSchema = Depends(get_current_user),
        # ) -> KanbanDefaultSettingsResponseSchema:
        #     """
        #     ## 📋 Получение настроек по умолчанию

        #     Возвращает настройки канбан-досок, используемые по умолчанию в системе.

        #     ### Args:
        #         * **workspace_id**: ID рабочего пространства

        #     ### Returns:
        #         * **data**: Объект с настройками по умолчанию
        #         * **message**: Сообщение о результате операции
        #     """
        #     return await kanban_service.get_default_settings(
        #         workspace_id=workspace_id,
        #         current_user=current_user,
        #     )

        # @self.router.post(
        #     path="/boards/{board_id}/settings/reset",
        #     response_model=KanbanBoardSettingsUpdateResponseSchema,
        #     responses={
        #         401: {"model": TokenMissingResponseSchema, "description": "Токен отсутствует"},
        #         403: {"model": KanbanAccessDeniedResponseSchema, "description": "Недостаточно прав для выполнения операции"},
        #         404: {"model": KanbanBoardNotFoundResponseSchema, "description": "Канбан-доска не найдена"},
        #     },
        # )
        # @inject
        # async def reset_kanban_board_settings(
        #     workspace_id: int,
        #     board_id: int = Path(..., description="ID канбан-доски"),
        #     kanban_service: FromDishka[KanbanService] = None,
        #     current_user: CurrentUserSchema = Depends(get_current_user),
        # ) -> KanbanBoardSettingsUpdateResponseSchema:
        #     """
        #     ## 🔄 Сброс настроек канбан-доски

        #     Сбрасывает настройки канбан-доски к значениям по умолчанию.

        #     ### Args:
        #     * **workspace_id**: ID рабочего пространства
        #     * **board_id**: ID канбан-доски

        #     ### Returns:
        #     * **data**: Сброшенные настройки канбан-доски
        #     * **message**: Сообщение о результате операции
        #     """
        #     return await kanban_service.reset_board_settings(
        #         board_id=board_id,
        #         current_user=current_user,
        #     )
