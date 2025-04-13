from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.v1.modules.tables import TableDefinitionModel
from app.schemas import TableDefinitionDataSchema, TableSchema
from app.services.v1.base import BaseEntityManager


class TableDataManager(BaseEntityManager[TableSchema]):
    """
    Менеджер данных для работы с таблицами.
    Реализует низкоуровневые операции для работы с таблицами.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session, schema=TableSchema, model=TableDefinitionModel
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
        table = TableDefinitionModel(
            workspace_id=workspace_id,
            name=name,
            description=description,
            table_schema=table_schema,
            display_settings={},  # Пустые настройки отображения по умолчанию
        )

        new_table = await self.add_one(table)

        return TableDefinitionDataSchema.model_validate(new_table)
