from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, WorkspaceNotFoundError
from app.models.v1.access import ResourceType
from app.models.v1.workspaces import WorkspaceModel, WorkspaceRole
from app.schemas import (CurrentUserSchema, PaginationParams,
                         TableDefinitionCreateResponseSchema,
                         TableDefinitionDeleteResponseSchema,
                         TableDefinitionResponseSchema,
                         TableDefinitionUpdateResponseSchema)
from app.services.v1.access.init import PolicyInitService
from app.services.v1.base import BaseService
from app.services.v1.modules.tables.data_manager import TableDataManager
from app.services.v1.workspaces.data_manager import WorkspaceDataManager
from app.services.v1.workspaces.service import WorkspaceService


class TableService(BaseService):
    """
    Сервис для управления таблицами
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.workspace_service = WorkspaceService(session)
        self.data_manager = TableDataManager(session)
        self.workspace_data_manager = WorkspaceDataManager(session)
        self.policy_init_service = PolicyInitService(self.session)

    async def create_table(
        self,
        workspace_id: int,
        name: str,
        description: str,
        table_schema: Dict[str, Any],
        current_user: CurrentUserSchema,
    ) -> TableDefinitionCreateResponseSchema:
        """
        Создает новую таблицу в рабочем пространстве

        Args:
            workspace_id: ID рабочего пространства
            name: Название таблицы
            description: Описание таблицы
            table_schema: Схема таблицы
            current_user: Текущий пользователь

        Returns:
            TableDefinitionCreateResponseSchema: Созданная таблица

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено
            ForbiddenError: Если у пользователя нет прав на создание таблицы
        """
        # Проверяем доступ к рабочему пространству (требуется роль EDITOR или выше)
        await self.workspace_service.check_workspace_access(
            workspace_id, current_user, WorkspaceRole.EDITOR
        )

        # Создание таблицы
        new_table = await self.data_manager.create_table(
            workspace_id=workspace_id,
            name=name,
            description=description,
            table_schema=table_schema,
        )

        # Применяем базовые правила доступа
        await self.policy_init_service.apply_default_resource_policy(
            resource_type=ResourceType.TABLE,
            resource_id=new_table.id,
            workspace_id=new_table.workspace_id,
            owner_id=current_user.id,
        )

        return TableDefinitionCreateResponseSchema(data=new_table)

    async def get_table(
        self, table_id: int, current_user: CurrentUserSchema
    ) -> TableDefinitionResponseSchema:
        """Получает таблицу по ID"""
        # Реализация...
        pass

    async def update_table(
        self, table_id: int, data: Dict[str, Any], current_user: CurrentUserSchema
    ) -> TableDefinitionUpdateResponseSchema:
        """Обновляет определение таблицы"""
        # Реализация...
        pass

    async def delete_table(
        self, table_id: int, current_user: CurrentUserSchema
    ) -> TableDefinitionDeleteResponseSchema:
        """Удаляет таблицу"""
        # Реализация...
        pass

    # async def create_row(self, table_id: int, data: Dict[str, Any], current_user: CurrentUserSchema) -> TableRowSchema:
    #     """Создает новую строку в таблице"""
    #     # Реализация...
    #     pass
    # async def get_rows(self, table_id: int, pagination: PaginationParams, current_user: CurrentUserSchema) -> Tuple[List[TableRowSchema], int]:
    #     """Получает строки таблицы с пагинацией"""
    #     # Реализация...
    #     pass
    # async def update_row(self, row_id: int, data: Dict[str, Any], current_user: CurrentUserSchema) -> TableRowSchema:
    #     """Обновляет строку таблицы"""
    #     # Реализация...
    #     pass
    # async def delete_row(self, row_id: int, current_user: CurrentUserSchema) -> bool:
    #     """Удаляет строку таблицы"""
    #     # Реализация...
    #     pass
    # async def create_from_template(self, workspace_id: int, template_id: int, current_user: CurrentUserSchema) -> TableDefinitionSchema:
    #     """Создает таблицу из шаблона"""
    #     # Реализация...
    #     pass
