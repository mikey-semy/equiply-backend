"""Маршруты для работы с канбан-досками."""

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Path, Query

from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.schemas.v1.modules.kanban.exceptions import (
    KanbanAccessDeniedResponseSchema,
    KanbanCardNotFoundResponseSchema, KanbanColumnNotFoundResponseSchema)
from app.schemas.v1.modules.kanban.requests import (
                                                    CreateKanbanCardSchema,
                                                    UpdateKanbanCardSchema,
                                                    MoveKanbanCardSchema)
from app.schemas.v1.modules.kanban.responses import (
    KanbanCardCreateResponseSchema,
    KanbanCardListResponseSchema, KanbanCardResponseSchema,
    KanbanCardUpdateResponseSchema, KanbanCardDeleteResponseSchema,
    KanbanCardMoveResponseSchema)
from app.schemas.v1.pagination import Page, PaginationParams
from app.schemas.v1.users import CurrentUserSchema
from app.services.v1.modules.kanban.service import KanbanService


class KanbanCardRouter(BaseRouter):
    """Маршруты для работы с канбан-карточками."""

    def __init__(self):
        super().__init__(prefix="workspaces/{workspace_id}/kanban", tags=["Kanban"])

    def configure(self):
        """Настройка маршрутов для канбан-досок."""

        @self.router.post(
            path="/columns/{column_id}/cards",
            response_model=KanbanCardCreateResponseSchema,
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
        async def create_kanban_card(
            workspace_id: int,
            column_id: int = Path(..., description="ID колонки"),
            card_data: CreateKanbanCardSchema = None,
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanCardCreateResponseSchema:
            """
            ## ➕ Создание карточки в колонке

            Создает новую карточку в колонке канбан-доски.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **column_id**: ID колонки

            ### Тело запроса:
            * **title**: Заголовок карточки
            * **description**: Описание карточки (опционально)
            * **order**: Порядок отображения карточки (опционально)
            * **data**: Дополнительные данные карточки (опционально)

            ### Returns:
            * **data**: Данные созданной карточки
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.create_card(
                column_id=column_id,
                card_data=card_data,
                current_user=current_user,
            )

        @self.router.get(
            path="/columns/{column_id}/cards",
            response_model=KanbanCardListResponseSchema,
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
        async def get_kanban_cards(
            workspace_id: int,
            column_id: int = Path(..., description="ID колонки"),
            kanban_service: FromDishka[KanbanService] = None,
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                50, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: str = Query("order", description="Поле для сортировки"),
            sort_desc: bool = Query(False, description="Сортировка по убыванию"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanCardListResponseSchema:
            """
            ## 📋 Получение списка карточек в колонке

            Возвращает список карточек в колонке канбан-доски с пагинацией.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **column_id**: ID колонки
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки (по умолчанию "order")
            * **sort_desc**: Сортировка по убыванию (по умолчанию False)

            ### Returns:
            * Страница с карточками колонки
            """
            pagination = PaginationParams(
                skip=skip,
                limit=limit,
                sort_by=sort_by,
                sort_desc=sort_desc,
                entity_name="KanbanCard"
            )

            cards, total = await kanban_service.get_cards(
                column_id=column_id,
                current_user=current_user,
                pagination=pagination,
            )
            page = Page(
                items=cards,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return KanbanCardListResponseSchema(data=page)

        @self.router.get(
            path="/cards/{card_id}",
            response_model=KanbanCardResponseSchema,
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
                    "model": KanbanCardNotFoundResponseSchema,
                    "description": "Карточка не найдена",
                },
            },
        )
        @inject
        async def get_kanban_card(
            workspace_id: int,
            card_id: int = Path(..., description="ID карточки"),
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanCardResponseSchema:
            """
            ## 🔍 Получение карточки канбан-доски

            Возвращает информацию о карточке канбан-доски по её ID.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **card_id**: ID карточки

            ### Returns:
            * **data**: Данные карточки
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.get_card(
                card_id=card_id,
                current_user=current_user,
            )

        @self.router.put(
            path="/cards/{card_id}",
            response_model=KanbanCardUpdateResponseSchema,
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
                    "model": KanbanCardNotFoundResponseSchema,
                    "description": "Карточка не найдена",
                },
            },
        )
        @inject
        async def update_kanban_card(
            workspace_id: int,
            card_id: int = Path(..., description="ID карточки"),
            card_data: UpdateKanbanCardSchema = None,
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanCardUpdateResponseSchema:
            """
            ## ✏️ Обновление карточки канбан-доски

            Обновляет информацию о карточке канбан-доски.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **card_id**: ID карточки

            ### Тело запроса:
            * **title**: Новый заголовок карточки (опционально)
            * **description**: Новое описание карточки (опционально)
            * **order**: Новый порядок отображения карточки (опционально)
            * **data**: Новые дополнительные данные карточки (опционально)

            ### Returns:
            * **data**: Данные обновленной карточки
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.update_card(
                card_id=card_id,
                card_data=card_data,
                current_user=current_user,
            )

        @self.router.delete(
            path="/cards/{card_id}",
            response_model=KanbanCardDeleteResponseSchema,
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
                    "model": KanbanCardNotFoundResponseSchema,
                    "description": "Карточка не найдена",
                },
            },
        )
        @inject
        async def delete_kanban_card(
            workspace_id: int,
            card_id: int = Path(..., description="ID карточки"),
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanCardDeleteResponseSchema:
            """
            ## 🗑️ Удаление карточки канбан-доски

            Удаляет карточку канбан-доски.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **card_id**: ID карточки

            ### Returns:
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.delete_card(
                card_id=card_id,
                current_user=current_user,
            )

        @self.router.put(
            path="/cards/{card_id}/move",
            response_model=KanbanCardMoveResponseSchema,
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
                    "model": KanbanCardNotFoundResponseSchema,
                    "description": "Карточка не найдена",
                },
            },
        )
        @inject
        async def move_kanban_card(
            workspace_id: int,
            card_id: int = Path(..., description="ID карточки"),
            move_data: MoveKanbanCardSchema = None,
            kanban_service: FromDishka[KanbanService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> KanbanCardMoveResponseSchema:
            """
            ## 🔄 Перемещение карточки

            Перемещает карточку между колонками или изменяет её порядок.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **card_id**: ID карточки

            ### Тело запроса:
            * **target_column_id**: ID целевой колонки (опционально, если перемещение в пределах текущей колонки)
            * **new_order**: Новый порядок отображения карточки

            ### Returns:
            * **data**: Данные перемещенной карточки
            * **message**: Сообщение о результате операции
            """
            return await kanban_service.move_card(
                card_id=card_id,
                move_data=move_data,
                current_user=current_user,
            )