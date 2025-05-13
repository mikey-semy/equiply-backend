from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy import and_, func, or_, select
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