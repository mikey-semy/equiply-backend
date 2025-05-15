from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy import and_, func, or_, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.v1.modules.tables import TableDefinitionModel
from app.schemas import PaginationParams, TableDefinitionDataSchema, TableSchema
from app.services.v1.base import BaseEntityManager


class TableDataManager(BaseEntityManager[TableSchema]):
    """
    Менеджер данных для работы с таблицами.
    Реализует низкоуровневые операции для работы с таблицами.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            schema=TableSchema,
            model=TableDefinitionModel
        )

    async def create_table(
        self,
        workspace_id: int,
        name: str,
        description: str,
        table_schema: Dict[str, Any],
    ) -> TableDefinitionDataSchema:
        """
        Создает новую таблицу

        Args:
            workspace_id: ID рабочего пространства
            name: Название таблицы
            description: Описание таблицы
            table_schema: Схема таблицы

        Returns:
            TableDefinitionDataSchema: Созданная таблица
        """
        table = self.model(
            workspace_id=workspace_id,
            name=name,
            description=description,
            table_schema=table_schema,
            display_settings={},  # Пустые настройки отображения по умолчанию
        )

        return await self.add_item(table)

    async def get_tables(
        self,
        workspace_id: int,
        pagination: PaginationParams = None,
        search: str = None,
    ) -> Tuple[List[TableDefinitionDataSchema], int]:
        """
        Получает список таблиц в рабочем пространстве.

        Args:
            workspace_id: ID рабочего пространства
            pagination: Параметры пагинации
            search: Строка поиска для фильтрации таблиц

        Returns:
            Tuple[List[TableDataSchema], int]: Список таблиц и общее количество
        """
        # Основной запрос для получения таблиц
        statement = select(self.model).where(self.model.workspace_id == workspace_id)

        # Если есть поисковый запрос, добавляем условие поиска
        if search:
            search_condition = or_(
                self.model.name.ilike(f"%{search}%"),
                self.model.description.ilike(f"%{search}%"),
            )
            statement = statement.where(search_condition)

        # Применяем пагинацию, если она указана
        if pagination:
            return await self.get_paginated_items(statement, pagination)

        return await self.get_items(statement)

    async def get_table(self, table_id: int) -> Optional[TableDefinitionDataSchema]:
        """
        Получает таблицу по ID.

        Args:
            table_id: ID таблицы

        Returns:
            TableDefinitionDataSchema: Найденная таблица или None
        """
        return await self.get_item(table_id)

    async def update_table(
        self,
        table_id: int,
        data: Dict[str, Any]
    ) -> Optional[TableDefinitionDataSchema]:
        """
        Обновляет таблицу по ID.

        Args:
            table_id: ID таблицы
            data: Словарь с данными для обновления

        Returns:
            TableDefinitionDataSchema: Обновленная таблица или None, если таблица не найдена
        """
        # Получаем таблицу
        statement = select(self.model).where(self.model.id == table_id)
        table = await self.get_one(statement)

        if not table:
            return None

        # Обновляем поля таблицы
        updated_table = await self.update_some(table, data)

        return TableDefinitionDataSchema.model_validate(updated_table)

    async def delete_table(self, table_id: int) -> bool:
        """
        Удаляет таблицу по ID.

        Args:
            table_id: ID таблицы

        Returns:
            bool: True, если таблица успешно удалена, иначе False
        """
        return await self.delete_item(table_id)

    async def get_table_rows(
        self,
        table_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Получает строки таблицы.

        Args:
            table_id: ID таблицы
            limit: Ограничение количества строк
            offset: Смещение для пагинации

        Returns:
            List[Dict[str, Any]]: Список строк таблицы
        """
        from app.models.v1.modules.tables import TableRowModel

        statement = select(TableRowModel).where(TableRowModel.table_definition_id == table_id)

        if limit is not None:
            statement = statement.limit(limit)
        if offset is not None:
            statement = statement.offset(offset)

        rows = await self.get_all(statement)
        return [row.data for row in rows]

    async def add_table_rows(
        self,
        table_id: int,
        rows: List[Dict[str, Any]]
    ) -> int:
        """
        Добавляет строки в таблицу.

        Args:
            table_id: ID таблицы
            rows: Список строк для добавления

        Returns:
            int: Количество добавленных строк
        """
        from app.models.v1.modules.tables import TableRowModel

        added_rows = []
        for row_data in rows:
            row = TableRowModel(table_definition_id=table_id, data=row_data)
            added_row = await self.add_one(row)
            added_rows.append(added_row)

        return len(added_rows)

    async def delete_table_rows(
        self,
        table_id: int
    ) -> bool:
        """
        Удаляет все строки таблицы.

        Args:
            table_id: ID таблицы

        Returns:
            bool: True, если строки успешно удалены
        """
        from app.models.v1.modules.tables import TableRowModel

        delete_statement = delete(TableRowModel).where(TableRowModel.table_definition_id == table_id)
        return await self.delete_one(delete_statement)
