from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, WorkspaceNotFoundError
from app.schemas import (
    PaginationParams,
    CurrentUserSchema,
    TableDefinitionResponseSchema,
    TableDefinitionCreateResponseSchema,
    TableDefinitionUpdateResponseSchema,
    TableDefinitionDeleteResponseSchema
)
from app.services.v1.base import BaseService
from app.services.v1.modules.tables.data_manager import TableDataManager
from app.models.v1.workspaces import WorkspaceModel, WorkspaceRole

class TableService(BaseService):
    """
    Сервис для управления таблицами
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.data_manager = TableDataManager(session)

    async def create_table(self, workspace_id: int, name: str, description: str,
                          schema: Dict[str, Any], current_user: CurrentUserSchema) -> TableDefinitionCreateResponseSchema:
        """
        Создает новую таблицу в рабочем пространстве

        Args:
            workspace_id: ID рабочего пространства
            name: Название таблицы
            description: Описание таблицы
            schema: Схема таблицы
            current_user: Текущий пользователь

        Returns:
            TableDefinitionCreateResponseSchema: Созданная таблица

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено
            ForbiddenError: Если у пользователя нет прав на создание таблицы
        """
        # # Проверка прав доступа
        # workspace = await self.data_manager.get_workspace(workspace_id)
        # if not workspace:
        #     raise WorkspaceNotFoundError(workspace_id)

        # # Проверка прав на создание таблицы
        # if not await self._can_modify_workspace(workspace, current_user):
        #     raise ForbiddenError("У вас нет прав на создание таблицы в этом рабочем пространстве")

        # # Создание таблицы
        # table = await self.data_manager.create_table(
        #     workspace_id=workspace_id,
        #     name=name,
        #     description=description,
        #     schema=schema
        # )

        # return TableDefinitionSchema.from_orm(table)
        pass

    async def get_table(self, table_id: int, current_user: CurrentUserSchema) -> TableDefinitionResponseSchema:
        """Получает таблицу по ID"""
        # Реализация...
        pass
    async def update_table(self, table_id: int, data: Dict[str, Any], current_user: CurrentUserSchema) -> TableDefinitionUpdateResponseSchema:
        """Обновляет определение таблицы"""
        # Реализация...
        pass
    async def delete_table(self, table_id: int, current_user: CurrentUserSchema) -> TableDefinitionDeleteResponseSchema:
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
    async def _can_modify_workspace(self, workspace: WorkspaceModel, user: CurrentUserSchema) -> bool:
        """Проверяет, может ли пользователь изменять рабочее пространство"""
        # Если пользователь владелец
        if workspace.owner_id == user.id:
            return True

        # Проверка роли пользователя в рабочем пространстве
        for member in workspace.members:
            if member.user_id == user.id:
                return member.role in [WorkspaceRole.ADMIN, WorkspaceRole.EDITOR]

        return False
