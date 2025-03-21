from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends

from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas import (CreateTableSchema, CurrentUserSchema,
                         TableDefinitionCreateResponseSchema)
from app.services.v1.modules.tables.service import TableService


class TableRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="tables", tags=["Tables"])

    def configure(self):
        @self.router.post(path="/", response_model=TableDefinitionCreateResponseSchema)
        @inject
        async def create_table(
            table_service: FromDishka[TableService],
            data: CreateTableSchema,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> TableDefinitionCreateResponseSchema:
            """Создает новую таблицу"""
            return await table_service.create_table(
                workspace_id=data.workspace_id,
                name=data.name,
                description=data.description,
                schema=data.schema,
                current_user=current_user,
            )
