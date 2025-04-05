"""Маршруты для работы с канбан-досками."""

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Path

from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.schemas.v1.modules.kanban.exceptions import (
    KanbanAccessDeniedResponseSchema, KanbanBoardNotFoundResponseSchema,
    KanbanColumnNotFoundResponseSchema)
from app.schemas.v1.modules.kanban.requests import (
                                                    CreateKanbanColumnSchema,
                                                    UpdateKanbanColumnSchema,
                                                    ReorderKanbanColumnsSchema,
                                                    )
from app.schemas.v1.modules.kanban.responses import (

    KanbanColumnCreateResponseSchema, KanbanColumnResponseSchema,
    KanbanColumnUpdateResponseSchema, KanbanColumnDeleteResponseSchema,
    KanbanColumnReorderResponseSchema)
from app.schemas.v1.users import CurrentUserSchema

from app.services.v1.modules.kanban.service import KanbanService


class KanbanColumnRouter(BaseRouter):
    """Маршруты для работы с канбан-досками."""

    def __init__(self):
        super().__init__(prefix="workspaces/{workspace_id}/kanban", tags=["Kanban"])

    def configure(self):
        """Настройка маршрутов для канбан-досок."""

        @self.router.post(
            path="/boards/{board_id}/columns",
            response_model=KanbanColumnCreateResponseSchema,
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
        async def create_kanban_column(
            workspace_id: int,
            board_id: int = Path(..., description="ID канбан-доски"),
            column_data: CreateKanbanColumnSchema = None,
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanColumnCreateResponseSchema:
            """
            ## ➕ Создание колонки в канбан-доске

            Создает новую колонку в канбан-доске.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **board_id**: ID канбан-доски

            ### Тело запроса:
            * **name**: Название колонки
            * **order**: Порядок отображения колонки (опционально)
            * **wip_limit**: Лимит работы в процессе (опционально)

            ### Returns:
            * **data**: Данные созданной колонки
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.create_column(
                board_id=board_id,
                column_data=column_data,
                current_user=current_user,
            )

        @self.router.get(
            path="/columns/{column_id}",
            response_model=KanbanColumnResponseSchema,
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
                    "model": KanbanColumnNotFoundResponseSchema,
                    "description": "Колонка не найдена",
                },
            },
        )
        @inject
        async def get_kanban_column(
            workspace_id: int,
            column_id: int = Path(..., description="ID колонки"),
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanColumnResponseSchema:
            """
            ## 🔍 Получение колонки канбан-доски

            Возвращает информацию о колонке канбан-доски по её ID.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **column_id**: ID колонки

            ### Returns:
            * **data**: Данные колонки
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.get_column(
                column_id=column_id,
                current_user=current_user,
            )

        @self.router.put(
            path="/columns/{column_id}",
            response_model=KanbanColumnUpdateResponseSchema,
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
                    "model": KanbanColumnNotFoundResponseSchema,
                    "description": "Колонка не найдена",
                },
            },
        )
        @inject
        async def update_kanban_column(
            workspace_id: int,
            column_id: int = Path(..., description="ID колонки"),
            column_data: UpdateKanbanColumnSchema = None,
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanColumnUpdateResponseSchema:
            """
            ## ✏️ Обновление колонки канбан-доски

            Обновляет информацию о колонке канбан-доски.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **column_id**: ID колонки

            ### Тело запроса:
            * **name**: Новое название колонки (опционально)
            * **order**: Новый порядок отображения колонки (опционально)
            * **wip_limit**: Новый лимит работы в процессе (опционально)

            ### Returns:
            * **data**: Данные обновленной колонки
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.update_column(
                column_id=column_id,
                column_data=column_data,
                current_user=current_user,
            )

        @self.router.delete(
            path="/columns/{column_id}",
            response_model=KanbanColumnDeleteResponseSchema,
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
                    "model": KanbanColumnNotFoundResponseSchema,
                    "description": "Колонка не найдена",
                },
            },
            )
        @inject
        async def delete_kanban_column(
            workspace_id: int,
            column_id: int = Path(..., description="ID колонки"),
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanColumnDeleteResponseSchema:
            """
            ## 🗑️ Удаление колонки канбан-доски

            Удаляет колонку канбан-доски и все связанные с ней карточки.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **column_id**: ID колонки

            ### Returns:
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.delete_column(
                column_id=column_id,
                current_user=current_user,
            )

        @self.router.put(
            path="/boards/{board_id}/columns/reorder",
            response_model=KanbanColumnReorderResponseSchema,
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
        async def reorder_kanban_columns(
            workspace_id: int,
            board_id: int = Path(..., description="ID канбан-доски"),
            reorder_data: ReorderKanbanColumnsSchema = None,
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanColumnReorderResponseSchema:
            """
            ## 🔄 Изменение порядка колонок

            Изменяет порядок колонок на канбан-доске.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **board_id**: ID канбан-доски

            ### Тело запроса:
            * **column_orders**: Список объектов с ID колонок и их новыми порядковыми номерами

            ### Returns:
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.reorder_columns(
                board_id=board_id,
                reorder_data=reorder_data,
                current_user=current_user,
            )
