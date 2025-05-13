from typing import Optional
from io import BytesIO
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Path, Query, File, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.core.security.access import require_permission
from app.core.security.auth import get_current_user
from app.models.v1.access import PermissionType, ResourceType
from app.routes.base import BaseRouter
from app.schemas.v1.pagination import Page, PaginationParams, TableSortFields
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.schemas import (CreateTableSchema, CurrentUserSchema,
                         TableDefinitionCreateResponseSchema,
                         TableDefinitionListResponseSchema,
                         TableDefinitionUpdateResponseSchema,
                         TableDefinitionDeleteResponseSchema,
                         TableDefinitionResponseSchema,
                         )
from app.services.v1.modules.tables.service import TableService


class TableRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="workspaces/{workspace_id}/tables", tags=["Tables"])

    def configure(self):
        """Настройка маршрутов для таблиц."""
        @self.router.post(
            path="/",
            response_model=TableDefinitionCreateResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": WorkspaceAccessDeniedResponseSchema,
                #     "description": "Недостаточно прав для выполнения операции",
                # },
                # 404: {
                #     "model": WorkspaceNotFoundResponseSchema,
                #     "description": "Рабочее пространство не найдено",
                # },
            },
        )
        @inject
        async def create_table(
            workspace_id: int,
            data: CreateTableSchema,
            table_service: FromDishka[TableService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> TableDefinitionCreateResponseSchema:
            """
            ## ➕ Создание таблицы

            Создает новую таблицу в рабочем пространстве.

            ### Args:
            * **workspace_id**: ID рабочего пространства

            ### Тело запроса:
            * **name**: Название таблицы
            * **description**: Описание таблицы (опционально)
            * **model_json_schema**: Схема таблицы

            ### Returns:
            * **data**: Данные созданной таблицы
            """
            return await table_service.create_table(
                workspace_id=workspace_id,
                name=data.name,
                description=data.description,
                table_schema=data.model_json_schema,
                current_user=current_user,
            )

        @self.router.get(
            path="/",
            response_model=Page[TableDefinitionResponseSchema],
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": WorkspaceAccessDeniedResponseSchema,
                #     "description": "Недостаточно прав для выполнения операции",
                # },
                # 404: {
                #     "model": WorkspaceNotFoundResponseSchema,
                #     "description": "Рабочее пространство не найдено",
                # },
            },
        )
        @inject
        async def get_tables(
            workspace_id: int,
            table_service: FromDishka[TableService],
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: Optional[str] = Query(
                TableSortFields.get_default().field,
                description=(
                    "Поле для сортировки пользователей. "
                    f"Доступные значения: {', '.join(TableSortFields.get_field_values())}. "
                    f"По умолчанию: {TableSortFields.get_default().field} "
                    f"({TableSortFields.get_default().description})."
                ),
                enum=TableSortFields.get_field_values(),
            ),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            search: Optional[str] = Query(
                None, description="Поиск по названию таблицы"
            ),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ):
            """
            ## 📋 Получение списка таблиц

            Возвращает список таблиц в рабочем пространстве с пагинацией и поиском.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки
            * **sort_desc**: Сортировка по убыванию
            * **search**: Поисковый запрос (опционально)

            ### Returns:
            * Страница с таблицами
            """
            pagination = PaginationParams(
                skip=skip,
                limit=limit,
                sort_by=sort_by,
                sort_desc=sort_desc,
                entity_name="Table",
            )
            tables, total = await table_service.get_tables(
                workspace_id=workspace_id,
                current_user=current_user,
                pagination=pagination,
                search=search,
            )

            page = Page(
                items=tables,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return TableDefinitionListResponseSchema(data=page)

        @self.router.get(
            path="/{table_id}",
            response_model=TableDefinitionResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": WorkspaceAccessDeniedResponseSchema,
                #     "description": "Недостаточно прав для выполнения операции",
                # },
                # 404: {
                #     "model": WorkspaceNotFoundResponseSchema,
                #     "description": "Таблица не найдена",
                # },
            },
        )
        @require_permission(
            resource_type=ResourceType.TABLE,
            permission=PermissionType.READ,
            resource_id_param="table_id"
        )
        @inject
        async def get_table(
            workspace_id: int,
            table_id: int = Path(..., description="ID таблицы"),
            table_service: FromDishka[TableService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> TableDefinitionResponseSchema:
            """
            ## 🔍 Получение таблицы

            Возвращает информацию о таблице по её ID.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **table_id**: ID таблицы

            ### Returns:
            * **data**: Данные таблицы
            * **message**: Сообщение о результате операции
            """
            return await table_service.get_table(
                workspace_id=workspace_id,
                table_id=table_id,
                current_user=current_user,
            )

        @self.router.put(
            path="/{table_id}",
            response_model=TableDefinitionUpdateResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": WorkspaceAccessDeniedResponseSchema,
                #     "description": "Недостаточно прав для выполнения операции",
                # },
                # 404: {
                #     "model": WorkspaceNotFoundResponseSchema,
                #     "description": "Таблица не найдена",
                # },
            },
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.WRITE,
            resource_id_param="table_id"
        )
        @inject
        async def update_table(
            workspace_id: int,
            table_id: int,
            data: CreateTableSchema,
            table_service: FromDishka[TableService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> TableDefinitionUpdateResponseSchema:
            """
            ## ✏️ Обновление таблицы

            Обновляет информацию о таблице.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **table_id**: ID таблицы

            ### Тело запроса:
            * **name**: Новое название таблицы (опционально)
            * **description**: Новое описание таблицы (опционально)
            * **model_json_schema**: Новая схема таблицы (опционально)

            ### Returns:
            * **data**: Данные обновленной таблицы
            """
            update_data = {
                "name": data.name,
                "description": data.description,
                "model_json_schema": data.model_json_schema,
            }
            return await table_service.update_table(
                workspace_id=workspace_id,
                table_id=table_id,
                data=update_data,
                current_user=current_user,
            )

        @self.router.delete(
            path="/{table_id}",
            response_model=TableDefinitionDeleteResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": WorkspaceAccessDeniedResponseSchema,
                #     "description": "Недостаточно прав для выполнения операции",
                # },
                # 404: {
                #     "model": WorkspaceNotFoundResponseSchema,
                #     "description": "Таблица не найдена",
                # },
            },
        )
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.DELETE,
            resource_id_param="table_id"
        )
        @inject
        async def delete_table(
            workspace_id: int,
            table_id: int = Path(..., description="ID таблицы"),
            table_service: FromDishka[TableService] = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> TableDefinitionDeleteResponseSchema:
            """
            ## 🗑️ Удаление таблицы

            Удаляет таблицу и все связанные с ней данные.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **table_id**: ID таблицы

            ### Returns:
            * **message**: Сообщение о результате операции
            """
            return await table_service.delete_table(
                workspace_id=workspace_id,
                table_id=table_id,
                current_user=current_user,
            )

        @self.router.post(
            path="/{table_id}/import",
            response_model=TableDefinitionUpdateResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
            },
        )
        @require_permission(
            resource_type=ResourceType.TABLE,
            permission=PermissionType.WRITE,
            resource_id_param="table_id"
        )
        @inject
        async def import_table_from_excel(
            workspace_id: int,
            table_service: FromDishka[TableService],
            table_id: int = Path(..., description="ID таблицы"),
            file: UploadFile = File(..., description="Excel файл для импорта"),
            background_tasks: BackgroundTasks = None,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> TableDefinitionUpdateResponseSchema:
            """
            ## 📥 Импорт данных из Excel

            Импортирует данные из Excel-файла в существующую таблицу.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **table_id**: ID таблицы
            * **file**: Excel-файл для импорта

            ### Returns:
            * **data**: Данные обновленной таблицы
            * **message**: Сообщение о результате операции
            """
            contents = await file.read()
            return await table_service.import_from_excel(
                workspace_id=workspace_id,
                table_id=table_id,
                file_contents=contents,
                filename=file.filename,
                background_tasks=background_tasks,
                current_user=current_user,
            )

        @self.router.get(
            path="/{table_id}/export",
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
            },
        )
        @require_permission(
            resource_type=ResourceType.TABLE,
            permission=PermissionType.READ,
            resource_id_param="table_id"
        )
        @inject
        async def export_table_to_excel(
            workspace_id: int,
            table_service: FromDishka[TableService],
            table_id: int = Path(..., description="ID таблицы"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ):
            """
            ## 📤 Экспорт данных в Excel

            Экспортирует данные таблицы в Excel-файл.

            ### Args:
            * **workspace_id**: ID рабочего пространства
            * **table_id**: ID таблицы

            ### Returns:
            * Excel-файл с данными таблицы
            """
            excel_data, filename = await table_service.export_to_excel(
                workspace_id=workspace_id,
                table_id=table_id,
                current_user=current_user,
            )

            return StreamingResponse(
                BytesIO(excel_data),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )