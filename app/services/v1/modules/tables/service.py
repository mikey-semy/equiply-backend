from typing import Any, Dict, List, Tuple, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TableNotFoundError
from app.core.integrations.storage.excel import ExcelS3DataManager
from app.models.v1.access import ResourceType
from app.models.v1.workspaces import WorkspaceRole
from app.schemas import (CurrentUserSchema, PaginationParams,
                         TableDefinitionDataSchema,
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

    def __init__(
        self,
        session: AsyncSession,
        s3_data_manager: Optional[ExcelS3DataManager] = None
    ):
        super().__init__(session)
        self.workspace_service = WorkspaceService(session)
        self.data_manager = TableDataManager(session)
        self.workspace_data_manager = WorkspaceDataManager(session)
        self.policy_init_service = PolicyInitService(self.session)
        self.s3_data_manager = s3_data_manager

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

    async def get_tables(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema,
        pagination: PaginationParams,
        search: str = None,
    ) -> Tuple[List[TableDefinitionDataSchema], int]:
        """
        Получает список таблиц в рабочем пространстве.

        Args:
            workspace_id: ID рабочего пространства
            current_user: Текущий пользователь
            pagination: Параметры пагинации для постраничной загрузки результатов
            search: Необязательная строка поиска для фильтрации таблиц

        Returns:
            Кортеж, содержащий список таблиц и общее количество доступных таблиц
        """
        self.logger.info(
            "Пользователь %s (ID: %s) запросил список таблиц в рабочем пространстве %s. "
            "Параметры: пагинация=%s, поиск='%s'",
            current_user.username,
            current_user.id,
            workspace_id,
            pagination,
            search,
        )

        return await self.data_manager.get_tables(
            workspace_id=workspace_id,
            pagination=pagination,
            search=search,
        )

    async def get_table(
        self,
        workspace_id: int,
        table_id: int,
        current_user: CurrentUserSchema
    ) -> TableDefinitionResponseSchema:
        """
        Получает таблицу по ID.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            current_user: Текущий пользователь

        Returns:
            TableDefinitionResponseSchema: Данные таблицы

        Raises:
            TableNotFoundError: Если таблица не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Получаем таблицу
        table = await self.data_manager.get_table(table_id)

        if not table:
            self.logger.error(
                "Таблица с ID %s не найдена при запросе пользователем %s (ID: %s)",
                table_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)  # Используем то же исключение для безопасности

        self.logger.info(
            "Пользователь %s (ID: %s) получил информацию о таблице %s (ID: %s) из рабочего пространства %s",
            current_user.username,
            current_user.id,
            table.name,
            table_id,
            workspace_id,
        )

        return TableDefinitionResponseSchema(data=table)


    async def update_table(
        self,
        workspace_id: int,
        table_id: int,
        data: Dict[str, Any],
        current_user: CurrentUserSchema
    ) -> TableDefinitionUpdateResponseSchema:
        """
        Обновляет определение таблицы.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            data: Данные для обновления
            current_user: Текущий пользователь

        Returns:
            TableDefinitionUpdateResponseSchema: Обновленная таблица

        Raises:
            TableNotFoundError: Если таблица не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Получаем таблицу для проверки существования и принадлежности к рабочему пространству
        table = await self.data_manager.get_table(table_id)

        if not table:
            self.logger.error(
                "Таблица с ID %s не найдена при попытке обновления пользователем %s (ID: %s)",
                table_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)  # Используем то же исключение для безопасности

        # Обновляем таблицу
        updated_table = await self.data_manager.update_table(table_id, data)

        self.logger.info(
            "Пользователь %s (ID: %s) обновил таблицу %s (ID: %s) в рабочем пространстве %s",
            current_user.username,
            current_user.id,
            updated_table.name,
            table_id,
            workspace_id,
        )

        return TableDefinitionUpdateResponseSchema(data=updated_table)

    async def delete_table(
        self,
        workspace_id: int,
        table_id: int,
        current_user: CurrentUserSchema
    ) -> TableDefinitionDeleteResponseSchema:
        """
        Удаляет таблицу.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            current_user: Текущий пользователь

        Returns:
            TableDefinitionDeleteResponseSchema: Результат удаления

        Raises:
            TableNotFoundError: Если таблица не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Получаем таблицу для проверки существования и принадлежности к рабочему пространству
        table = await self.data_manager.get_table(table_id)

        if not table:
            self.logger.error(
                "Таблица с ID %s не найдена при попытке удаления пользователем %s (ID: %s)",
                table_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)  # Используем то же исключение для безопасности

        # Удаляем таблицу
        success = await self.data_manager.delete_table(table_id)

        if not success:
            self.logger.error(
                "Не удалось удалить таблицу с ID %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        self.logger.info(
            "Пользователь %s (ID: %s) удалил таблицу с ID %s из рабочего пространства %s",
            current_user.username,
            current_user.id,
            table_id,
            workspace_id,
        )

        return TableDefinitionDeleteResponseSchema(
            message=f"Таблица с ID {table_id} успешно удалена"
        )

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
