"""
Менеджер данных для работы с канбан-досками.
"""

from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy import and_, func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload


from app.models.v1.modules.kanban import KanbanBoardModel, KanbanColumnModel, KanbanCardModel
from app.schemas.v1.modules.kanban.base import KanbanBoardDetailDataSchema, KanbanColumnDataSchema, KanbanCardDataSchema
from app.schemas.v1.pagination import PaginationParams
from app.services.v1.base import BaseEntityManager


class KanbanDataManager:
    """
    Менеджер данных для работы с канбан-досками.

    Предоставляет методы для выполнения операций с базой данных,
    связанных с канбан-досками, колонками и карточками.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует менеджер данных.

        Args:
            session: Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        self.session = session
        self.board_manager = KanbanBoardManager(session)
        self.column_manager = KanbanColumnManager(session)
        self.card_manager = KanbanCardManager(session)

    # Методы для работы с досками
    async def get_board(self, board_id: int) -> Optional[KanbanBoardModel]:
        """
        Получает канбан-доску по ID.

        Args:
            board_id: ID канбан-доски.

        Returns:
            KanbanBoardModel или None, если доска не найдена.
        """
        return await self.board_manager.get_model_by_field("id", board_id)

    async def get_boards(
        self, workspace_id: int, pagination: PaginationParams, search: Optional[str] = None
    ) -> Tuple[List[KanbanBoardModel], int]:
        """
        Получает список канбан-досок для рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства.
            pagination: Параметры пагинации.
            search: Строка поиска (поиск по имени доски).

        Returns:
            Кортеж (список канбан-досок, общее количество).
        """
        statement = select(KanbanBoardModel).where(
            KanbanBoardModel.workspace_id == workspace_id
        )

        if search:
            statement = statement.where(
                KanbanBoardModel.name.ilike(f"%{search}%")
            )

        return await self.board_manager.get_paginated_items(
            statement, pagination, KanbanBoardDetailDataSchema
        )

    async def get_board_with_details(self, board_id: int) -> Optional[KanbanBoardDetailDataSchema]:
        """
        Получает детальную информацию о канбан-доске, включая колонки и карточки.

        Args:
            board_id: ID канбан-доски.

        Returns:
            KanbanBoardDetailDataSchema или None, если доска не найдена.
        """
        statement = select(KanbanBoardModel).where(
            KanbanBoardModel.id == board_id
        ).options(
            selectinload(KanbanBoardModel.columns).selectinload(KanbanColumnModel.cards)
        )

        board = await self.session.execute(statement)
        board_model = board.scalars().first()

        if not board_model:
            return None

        return KanbanBoardDetailDataSchema.model_validate(board_model)

    async def create_board(
        self, workspace_id: int, name: str, description: Optional[str] = None,
        display_settings: Optional[Dict[str, Any]] = None,
        template_id: Optional[int] = None
    ) -> KanbanBoardModel:
        """
        Создает новую канбан-доску.

        Args:
            workspace_id: ID рабочего пространства.
            name: Название доски.
            description: Описание доски.
            display_settings: Настройки отображения доски.
            template_id: ID шаблона модуля (если есть).

        Returns:
            Созданная канбан-доска.
        """
        board = KanbanBoardModel(
            workspace_id=workspace_id,
            name=name,
            description=description,
            display_settings=display_settings or {},
            template_id=template_id
        )

        return await self.board_manager.add_one(board)

    async def update_board(
        self, board_id: int, name: Optional[str] = None,
        description: Optional[str] = None,
        display_settings: Optional[Dict[str, Any]] = None
    ) -> Optional[KanbanBoardModel]:
        """
        Обновляет канбан-доску.

        Args:
            board_id: ID канбан-доски.
            name: Новое название доски.
            description: Новое описание доски.
            display_settings: Новые настройки отображения доски.

        Returns:
            Обновленная канбан-доска или None, если доска не найдена.
        """
        board = await self.get_board(board_id)
        if not board:
            return None

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if display_settings is not None:
            update_data["display_settings"] = display_settings

        if update_data:
            await self.board_manager.update_some(board, update_data)

        return board

    async def delete_board(self, board_id: int) -> bool:
        """
        Удаляет канбан-доску.

        Args:
            board_id: ID канбан-доски.

        Returns:
            True, если доска успешно удалена, иначе False.
        """
        statement = delete(KanbanBoardModel).where(KanbanBoardModel.id == board_id)
        return await self.board_manager.delete_one(statement)

    # Методы для работы с колонками
    async def get_column(self, column_id: int) -> Optional[KanbanColumnModel]:
        """
        Получает колонку канбан-доски по ID.

        Args:
            column_id: ID колонки.

        Returns:
            KanbanColumnModel или None, если колонка не найдена.
        """
        return await self.column_manager.get_model_by_field("id", column_id)

    async def get_columns(
        self, board_id: int, pagination: PaginationParams
    ) -> Tuple[List[KanbanColumnModel], int]:
        """
        Получает список колонок для канбан-доски.

        Args:
            board_id: ID канбан-доски.
            pagination: Параметры пагинации.

        Returns:
            Кортеж (список колонок, общее количество).
        """
        statement = select(KanbanColumnModel).where(
            KanbanColumnModel.board_id == board_id
        ).order_by(KanbanColumnModel.order)

        return await self.column_manager.get_paginated_items(
            statement, pagination, KanbanColumnDataSchema
        )

    async def create_column(
        self, board_id: int, name: str, order: int, wip_limit: Optional[int] = None
    ) -> KanbanColumnModel:
        """
        Создает новую колонку канбан-доски.

        Args:
            board_id: ID канбан-доски.
            name: Название колонки.
            order: Порядок колонки на доске.
            wip_limit: Лимит работы в процессе.

        Returns:
            Созданная колонка.
        """
        column = KanbanColumnModel(
            board_id=board_id,
            name=name,
            order=order,
            wip_limit=wip_limit
        )

        return await self.column_manager.add_one(column)

    async def update_column(
        self, column_id: int, name: Optional[str] = None,
        order: Optional[int] = None, wip_limit: Optional[int] = None
    ) -> Optional[KanbanColumnModel]:
        """
        Обновляет колонку канбан-доски.

        Args:
            column_id: ID колонки.
            name: Новое название колонки.
            order: Новый порядок колонки.
            wip_limit: Новый лимит работы в процессе.

        Returns:
            Обновленная колонка или None, если колонка не найдена.
        """
        column = await self.get_column(column_id)
        if not column:
            return None

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if order is not None:
            update_data["order"] = order
        if wip_limit is not None:
            update_data["wip_limit"] = wip_limit

        if update_data:
            await self.column_manager.update_some(column, update_data)

        return column

    async def reorder_columns(self, board_id: int, column_orders: Dict[int, int]) -> bool:
        """
        Переупорядочивает колонки канбан-доски.

        Args:
            board_id: ID канбан-доски.
            column_orders: Словарь с ID колонок и их новыми порядками.

        Returns:
            True, если колонки успешно переупорядочены, иначе False.
        """

        # Проверяем существование доски
        board = await self.get_board(board_id)
        if not board:
            return False

        # Получаем все колонки доски
        statement = select(KanbanColumnModel).where(
            KanbanColumnModel.board_id == board_id
        )
        columns = await self.column_manager.get_all(statement)

        # Проверяем, что все ID колонок из column_orders существуют на доске
        column_ids = {column.id for column in columns}
        for column_id in column_orders.keys():
            if column_id not in column_ids:
                return False

        # Обновляем порядок колонок
        for column_id, order in column_orders.items():
            for column in columns:
                if column.id == column_id:
                    await self.column_manager.update_some(column, {"order": order})
                    break

        return True

    async def delete_column(self, column_id: int) -> bool:
        """
        Удаляет колонку канбан-доски.

        Args:
            column_id: ID колонки.

        Returns:
            True, если колонка успешно удалена, иначе False.
        """
        statement = delete(KanbanColumnModel).where(KanbanColumnModel.id == column_id)
        return await self.column_manager.delete_one(statement)

    # Методы для работы с карточками
    async def get_card(self, card_id: int) -> Optional[KanbanCardModel]:
        """
        Получает карточку канбан-доски по ID.

        Args:
            card_id: ID карточки.

        Returns:
            KanbanCardModel или None, если карточка не найдена.
        """
        return await self.card_manager.get_model_by_field("id", card_id)

    async def get_cards(
        self, column_id: int, pagination: PaginationParams
    ) -> Tuple[List[KanbanCardModel], int]:
        """
        Получает список карточек для колонки канбан-доски.

        Args:
            column_id: ID колонки.
            pagination: Параметры пагинации.

        Returns:
            Кортеж (список карточек, общее количество).
        """
        statement = select(KanbanCardModel).where(
            KanbanCardModel.column_id == column_id
        ).order_by(KanbanCardModel.order)

        return await self.card_manager.get_paginated_items(
            statement, pagination, KanbanCardDataSchema
        )

    async def create_card(
        self, column_id: int, title: str, description: Optional[str] = None,
        order: int = 0, data: Optional[Dict[str, Any]] = None
    ) -> KanbanCardModel:
        """
        Создает новую карточку канбан-доски.

        Args:
            column_id: ID колонки.
            title: Заголовок карточки.
            description: Описание карточки.
            order: Порядок карточки в колонке.
            data: Дополнительные данные карточки.

        Returns:
            Созданная карточка.
        """
        card = KanbanCardModel(
            column_id=column_id,
            title=title,
            description=description,
            order=order,
            data=data or {}
        )

        return await self.card_manager.add_one(card)

    async def update_card(
        self, card_id: int, title: Optional[str] = None,
        description: Optional[str] = None, order: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None, column_id: Optional[int] = None
    ) -> Optional[KanbanCardModel]:
        """
        Обновляет карточку канбан-доски.

        Args:
            card_id: ID карточки.
            title: Новый заголовок карточки.
            description: Новое описание карточки.
            order: Новый порядок карточки.
            data: Новые дополнительные данные карточки.
            column_id: ID новой колонки (для перемещения карточки).

        Returns:
            Обновленная карточка или None, если карточка не найдена.
        """
        card = await self.get_card(card_id)
        if not card:
            return None

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if order is not None:
            update_data["order"] = order
        if data is not None:
            update_data["data"] = data
        if column_id is not None:
            update_data["column_id"] = column_id

        if update_data:
            await self.card_manager.update_some(card, update_data)

        return card

    async def delete_card(self, card_id: int) -> bool:
        """
        Удаляет карточку канбан-доски.

        Args:
            card_id: ID карточки.

        Returns:
            True, если карточка успешно удалена, иначе False.
        """
        statement = delete(KanbanCardModel).where(KanbanCardModel.id == card_id)
        return await self.card_manager.delete_one(statement)

    async def move_card(
        self, card_id: int, target_column_id: int, new_order: int
    ) -> Optional[KanbanCardModel]:
        """
        Перемещает карточку в другую колонку и/или изменяет её порядок.

        Args:
            card_id: ID карточки.
            target_column_id: ID целевой колонки.
            new_order: Новый порядок карточки в колонке.

        Returns:
            Обновленная карточка или None, если карточка не найдена.
        """
        return await self.update_card(
            card_id=card_id,
            column_id=target_column_id,
            order=new_order
        )


class KanbanBoardManager(BaseEntityManager[KanbanBoardDetailDataSchema]):
    """Менеджер данных для работы с канбан-досками."""

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            schema=KanbanBoardDetailDataSchema,
            model=KanbanBoardModel
        )


class KanbanColumnManager(BaseEntityManager[KanbanColumnDataSchema]):
    """Менеджер данных для работы с колонками канбан-досок."""

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            schema=KanbanColumnDataSchema,
            model=KanbanColumnModel
        )


class KanbanCardManager(BaseEntityManager[KanbanCardDataSchema]):
    """Менеджер данных для работы с карточками канбан-досок."""

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            schema=KanbanCardDataSchema,
            model=KanbanCardModel
        )
