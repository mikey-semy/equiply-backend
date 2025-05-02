from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (KanbanBoardAccessDeniedError,
                                 KanbanBoardNotFoundError,
                                 KanbanCardNotFoundError,
                                 KanbanColumnNotFoundError,
                                 WorkspaceAccessDeniedError,
                                 WorkspaceNotFoundError)
from app.models.v1.workspaces import WorkspaceRole
from app.schemas.v1.modules.kanban.base import (KanbanBoardDataSchema,
                                                KanbanCardDataSchema,
                                                KanbanColumnDataSchema)
from app.schemas.v1.modules.kanban.requests import (CreateKanbanBoardSchema,
                                                    CreateKanbanCardSchema,
                                                    CreateKanbanColumnSchema,
                                                    MoveKanbanCardSchema,
                                                    ReorderKanbanColumnsSchema,
                                                    UpdateKanbanBoardSchema,
                                                    UpdateKanbanCardSchema,
                                                    UpdateKanbanColumnSchema)
from app.schemas.v1.modules.kanban.responses import (
    KanbanBoardCreateResponseSchema, KanbanBoardDeleteResponseSchema,
    KanbanBoardDetailResponseSchema, KanbanBoardResponseSchema,
    KanbanBoardUpdateResponseSchema, KanbanCardCreateResponseSchema,
    KanbanCardDeleteResponseSchema, KanbanCardMoveResponseSchema,
    KanbanCardResponseSchema, KanbanCardUpdateResponseSchema,
    KanbanColumnCreateResponseSchema, KanbanColumnDeleteResponseSchema,
    KanbanColumnReorderResponseSchema, KanbanColumnResponseSchema,
    KanbanColumnUpdateResponseSchema)
from app.schemas.v1.pagination import PaginationParams
from app.schemas.v1.users import CurrentUserSchema
from app.services.v1.base import BaseService
from app.services.v1.modules.kanban.data_manager import KanbanDataManager
from app.services.v1.workspaces.data_manager import WorkspaceDataManager
from app.services.v1.workspaces.service import WorkspaceService


class KanbanService(BaseService):
    """
    Сервис для работы с канбан-досками.

    Предоставляет методы для создания, получения, обновления и удаления
    канбан-досок, колонок и карточек.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис канбан-досок.

        Args:
            session: Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        super().__init__(session)
        self.workspace_service = WorkspaceService(session)
        self.data_manager = KanbanDataManager(session)
        self.workspace_data_manager = WorkspaceDataManager(session)

    async def _check_board_access(self, board_id: int, user_id: int) -> bool:
        """
        Проверяет доступ пользователя к канбан-доске.

        Args:
            board_id: ID канбан-доски.
            user_id: ID пользователя.

        Returns:
            bool: True, если пользователь имеет доступ к канбан-доске.

        Raises:
            KanbanBoardNotFoundError: Если канбан-доска не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет доступа к канбан-доске.
        """
        board = await self.data_manager.get_board(board_id)
        if not board:
            raise KanbanBoardNotFoundError(board_id)

        # Проверяем доступ к рабочему пространству, в котором находится доска
        # оборачиваем в CurrentUserSchema, чтобы передать в check_workspace_access
        current_user = CurrentUserSchema(id=user_id, username="", email="")
        await self.workspace_service.check_workspace_access(
            board.workspace_id, current_user, WorkspaceRole.EDITOR
        )

        return True

    async def create_board(
        self,
        workspace_id: int,
        board_data: CreateKanbanBoardSchema,
        current_user: CurrentUserSchema,
    ) -> KanbanBoardCreateResponseSchema:
        """
        Создает новую канбан-доску в рабочем пространстве.

        Args:
            workspace_id: ID рабочего пространства.
            board_data: Данные для создания канбан-доски.
            current_user: Текущий пользователь.

        Returns:
            KanbanBoardCreateResponseSchema: Данные созданной канбан-доски.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству.
        """
        # Проверка прав доступа (требуется роль EDITOR или выше)
        await self.workspace_service.check_workspace_access(
            workspace_id, current_user, WorkspaceRole.EDITOR
        )

        # Создаем канбан-доску
        board = await self.data_manager.create_board(
            workspace_id=workspace_id,
            name=board_data.name,
            description=board_data.description,
            display_settings=board_data.display_settings,
            template_id=board_data.template_id,
        )

        # Логируем создание доски
        self.logger.info(
            "Создана канбан-доска '%s' (ID: %s) в рабочем пространстве %s пользователем %s (ID: %s)",
            board_data.name,
            board.id,
            workspace_id,
            current_user.username,
            current_user.id,
        )

        return KanbanBoardCreateResponseSchema(data=board)

    async def get_boards(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema,
        pagination: PaginationParams,
        search: Optional[str] = None,
    ) -> Tuple[List[KanbanBoardDataSchema], int]:
        """
        Получает список канбан-досок в рабочем пространстве.

        Args:
            workspace_id: ID рабочего пространства.
            current_user: Текущий пользователь.
            pagination: Параметры пагинации.
            search: Строка поиска.

        Returns:
            Tuple[List[KanbanBoardDataSchema], int]: Список канбан-досок и общее количество.

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено.
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству.
        """
        # Проверяем доступ к рабочему пространству
        await self.workspace_service.check_workspace_access(
            workspace_id, current_user, WorkspaceRole.VIEWER
        )

        self.logger.info(
            "Пользователь %s (ID: %s) запросил список канбан-досок в рабочем пространстве %s. \
            Параметры: пагинация=%s, поиск='%s'",
            current_user.username,
            current_user.id,
            workspace_id,
            pagination,
            search,
        )

        return await self.data_manager.get_boards(
            workspace_id=workspace_id, pagination=pagination, search=search
        )

    async def get_board(
        self, board_id: int, current_user: CurrentUserSchema
    ) -> KanbanBoardResponseSchema:
        """
        Получает канбан-доску по ID.

        Args:
            board_id: ID канбан-доски.
            current_user: Текущий пользователь.

        Returns:
            KanbanBoardResponseSchema: Данные канбан-доски.

        Raises:
            KanbanBoardNotFoundError: Если канбан-доска не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет доступа к канбан-доске.
        """
        # Проверяем доступ к канбан-доске
        await self._check_board_access(board_id, current_user.id)

        board = await self.data_manager.get_board(board_id)

        self.logger.info(
            "Пользователь %s (ID: %s) получил канбан-доску %s",
            current_user.username,
            current_user.id,
            board_id,
        )

        return KanbanBoardResponseSchema(
            data=KanbanBoardDataSchema.model_validate(board)
        )

    async def get_board_details(
        self, board_id: int, current_user: CurrentUserSchema
    ) -> KanbanBoardDetailResponseSchema:
        """
        Получает детальную информацию о канбан-доске, включая колонки и карточки.

        Args:
            board_id: ID канбан-доски.
            current_user: Текущий пользователь.

        Returns:
            KanbanBoardDetailResponseSchema: Детальные данные канбан-доски.

        Raises:
            KanbanBoardNotFoundError: Если канбан-доска не найдена.
            KanbanAccessDeniedError: Если у пользователя нет доступа к канбан-доске.
        """
        # Проверяем доступ к канбан-доске
        await self._check_board_access(board_id, current_user.id)

        board_with_details = await self.data_manager.get_board_with_details(board_id)

        self.logger.info(
            "Пользователь %s (ID: %s) получил детальную информацию о канбан-доске %s",
            current_user.username,
            current_user.id,
            board_id,
        )

        return KanbanBoardDetailResponseSchema(data=board_with_details)

    async def update_board(
        self,
        board_id: int,
        board_data: UpdateKanbanBoardSchema,
        current_user: CurrentUserSchema,
    ) -> KanbanBoardUpdateResponseSchema:
        """
        Обновляет канбан-доску.

        Args:
            board_id: ID канбан-доски.
            board_data: Данные для обновления канбан-доски.
            current_user: Текущий пользователь.

        Returns:
            KanbanBoardUpdateResponseSchema: Данные обновленной канбан-доски.

        Raises:
            KanbanBoardNotFoundError: Если канбан-доска не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет доступа к канбан-доске.
        """
        # Проверяем доступ к канбан-доске
        board = await self.data_manager.get_board(board_id)
        if not board:
            raise KanbanBoardNotFoundError(board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board_id, "У вас нет прав на обновление канбан-доски"
            )

        # Обновляем канбан-доску
        updated_board = await self.data_manager.update_board(board_id, board_data)

        self.logger.info(
            "Пользователь %s (ID: %s) обновил канбан-доску %s",
            current_user.username,
            current_user.id,
            board_id,
        )

        return KanbanBoardUpdateResponseSchema(data=updated_board)

    async def delete_board(
        self, board_id: int, current_user: CurrentUserSchema
    ) -> KanbanBoardDeleteResponseSchema:
        """
        Удаляет канбан-доску.

        Args:
            board_id: ID канбан-доски.
            current_user: Текущий пользователь.

        Returns:
            KanbanBoardDeleteResponseSchema: Сообщение об успешном удалении.

        Raises:
            KanbanBoardNotFoundError: Если канбан-доска не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на удаление канбан-доски.
        """
        # Проверяем доступ к канбан-доске
        board = await self.data_manager.get_board(board_id)
        if not board:
            raise KanbanBoardNotFoundError(board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.ADMIN
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board_id, "У вас нет прав на удаление канбан-доски"
            )

        # Удаляем канбан-доску
        await self.data_manager.delete_board(board_id)

        self.logger.info(
            "Пользователь %s (ID: %s) удалил канбан-доску %s",
            current_user.username,
            current_user.id,
            board_id,
        )

        return KanbanBoardDeleteResponseSchema()

    # Методы для работы с колонками

    async def create_column(
        self,
        board_id: int,
        column_data: CreateKanbanColumnSchema,
        current_user: CurrentUserSchema,
    ) -> KanbanColumnCreateResponseSchema:
        """
        Создает новую колонку в канбан-доске.

        Args:
            board_id: ID канбан-доски.
            column_data: Данные для создания колонки.
            current_user: Текущий пользователь.

        Returns:
            KanbanColumnCreateResponseSchema: Данные созданной колонки.

        Raises:
            KanbanBoardNotFoundError: Если канбан-доска не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на редактирование доски.
        """
        # Проверяем доступ к канбан-доске
        board = await self.data_manager.get_board(board_id)
        if not board:
            raise KanbanBoardNotFoundError(board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board_id, "У вас нет прав на редактирование канбан-доски"
            )

        # Создаем колонку
        column = await self.data_manager.create_column(
            board_id=board_id,
            name=column_data.name,
            order=column_data.order,
            wip_limit=column_data.wip_limit,
        )

        self.logger.info(
            "Пользователь %s (ID: %s) создал колонку '%s' (ID: %s) в канбан-доске %s",
            current_user.username,
            current_user.id,
            column_data.name,
            column.id,
            board_id,
        )

        return KanbanColumnCreateResponseSchema(data=column)

    async def get_columns(
        self,
        board_id: int,
        current_user: CurrentUserSchema,
        pagination: PaginationParams,
    ) -> Tuple[List[KanbanColumnDataSchema], int]:
        """
        Получает список колонок канбан-доски.

        Args:
            board_id: ID канбан-доски.
            current_user: Текущий пользователь.
            pagination: Параметры пагинации.

        Returns:
            Tuple[List[KanbanColumnDataSchema], int]: Список колонок и общее количество.

        Raises:
            KanbanBoardNotFoundError: Если канбан-доска не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет доступа к канбан-доске.
        """
        # Проверяем доступ к канбан-доске
        await self._check_board_access(board_id, current_user.id)

        self.logger.info(
            "Пользователь %s (ID: %s) запросил список колонок канбан-доски %s",
            current_user.username,
            current_user.id,
            board_id,
        )

        return await self.data_manager.get_columns(
            board_id=board_id, pagination=pagination
        )

    async def get_column(
        self, column_id: int, current_user: CurrentUserSchema
    ) -> KanbanColumnResponseSchema:
        """
        Получает колонку канбан-доски по ID.

        Args:
            column_id: ID колонки.
            current_user: Текущий пользователь.

        Returns:
            KanbanColumnResponseSchema: Данные колонки.

        Raises:
            KanbanColumnNotFoundError: Если колонка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет доступа к канбан-доске.
        """
        # Получаем колонку
        column = await self.data_manager.get_column(column_id)
        if not column:
            raise KanbanColumnNotFoundError(column_id)

        # Проверяем доступ к канбан-доске
        await self.workspace_service.check_workspace_access(
            column.board_id, current_user, WorkspaceRole.VIEWER
        )

        self.logger.info(
            "Пользователь %s (ID: %s) получил колонку %s",
            current_user.username,
            current_user.id,
            column_id,
        )

        return KanbanColumnResponseSchema(
            data=KanbanColumnDataSchema.model_validate(column)
        )

    async def update_column(
        self,
        column_id: int,
        column_data: UpdateKanbanColumnSchema,
        current_user: CurrentUserSchema,
    ) -> KanbanColumnUpdateResponseSchema:
        """
        Обновляет колонку канбан-доски.

        Args:
            column_id: ID колонки.
            column_data: Данные для обновления колонки.
            current_user: Текущий пользователь.

        Returns:
            KanbanColumnUpdateResponseSchema: Данные обновленной колонки.

        Raises:
            KanbanColumnNotFoundError: Если колонка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на редактирование доски.
        """
        # Получаем колонку
        column = await self.data_manager.get_column(column_id)
        if not column:
            raise KanbanColumnNotFoundError(column_id)

        # Получаем доску
        board = await self.data_manager.get_board(column.board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board.id, "У вас нет прав на редактирование канбан-доски"
            )

        # Обновляем колонку
        updated_column = await self.data_manager.update_column(column_id, column_data)

        self.logger.info(
            "Пользователь %s (ID: %s) обновил колонку %s",
            current_user.username,
            current_user.id,
            column_id,
        )

        return KanbanColumnUpdateResponseSchema(data=updated_column)

    async def delete_column(
        self, column_id: int, current_user: CurrentUserSchema
    ) -> KanbanColumnDeleteResponseSchema:
        """
        Удаляет колонку канбан-доски.

        Args:
            column_id: ID колонки.
            current_user: Текущий пользователь.

        Returns:
            KanbanColumnDeleteResponseSchema: Сообщение об успешном удалении.

        Raises:
            KanbanColumnNotFoundError: Если колонка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на редактирование доски.
        """
        # Получаем колонку
        column = await self.data_manager.get_column(column_id)
        if not column:
            raise KanbanColumnNotFoundError(column_id)

        # Получаем доску
        board = await self.data_manager.get_board(column.board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board.id, "У вас нет прав на редактирование канбан-доски"
            )

        # Удаляем колонку
        await self.data_manager.delete_column(column_id)

        self.logger.info(
            "Пользователь %s (ID: %s) удалил колонку %s",
            current_user.username,
            current_user.id,
            column_id,
        )

        return KanbanColumnDeleteResponseSchema()

    async def reorder_columns(
        self,
        board_id: int,
        reorder_data: ReorderKanbanColumnsSchema,
        current_user: CurrentUserSchema,
    ) -> KanbanColumnReorderResponseSchema:
        """
        Изменяет порядок колонок на канбан-доске.

        Args:
            board_id: ID канбан-доски.
            reorder_data: Данные для изменения порядка колонок.
            current_user: Текущий пользователь.

        Returns:
            KanbanColumnReorderResponseSchema: Сообщение об успешном изменении порядка.

        Raises:
            KanbanBoardNotFoundError: Если канбан-доска не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на редактирование доски.
        """
        # Проверяем доступ к канбан-доске
        board = await self.data_manager.get_board(board_id)
        if not board:
            raise KanbanBoardNotFoundError(board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board_id, "У вас нет прав на редактирование канбан-доски"
            )

        # Изменяем порядок колонок
        await self.data_manager.reorder_columns(board_id, reorder_data.column_orders)

        self.logger.info(
            "Пользователь %s (ID: %s) изменил порядок колонок на канбан-доске %s",
            current_user.username,
            current_user.id,
            board_id,
        )

        return KanbanColumnReorderResponseSchema()

    # Методы для работы с карточками

    async def create_card(
        self,
        column_id: int,
        card_data: CreateKanbanCardSchema,
        current_user: CurrentUserSchema,
    ) -> KanbanCardCreateResponseSchema:
        """
        Создает новую карточку в колонке канбан-доски.

        Args:
            column_id: ID колонки.
            card_data: Данные для создания карточки.
            current_user: Текущий пользователь.

        Returns:
            KanbanCardCreateResponseSchema: Данные созданной карточки.

        Raises:
            KanbanColumnNotFoundError: Если колонка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на редактирование доски.
        """
        # Получаем колонку
        column = await self.data_manager.get_column(column_id)
        if not column:
            raise KanbanColumnNotFoundError(column_id)

        # Получаем доску
        board = await self.data_manager.get_board(column.board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board.id, "У вас нет прав на редактирование канбан-доски"
            )

        # Создаем карточку
        card = await self.data_manager.create_card(
            column_id=column_id,
            title=card_data.title,
            description=card_data.description,
            order=card_data.order,
            data=card_data.data,
        )

        self.logger.info(
            "Пользователь %s (ID: %s) создал карточку '%s' (ID: %s) в колонке %s",
            current_user.username,
            current_user.id,
            card_data.title,
            card.id,
            column_id,
        )

        return KanbanCardCreateResponseSchema(data=card)

    async def get_cards(
        self,
        column_id: int,
        current_user: CurrentUserSchema,
        pagination: PaginationParams,
    ) -> Tuple[List[KanbanCardDataSchema], int]:
        """
        Получает список карточек в колонке канбан-доски.

        Args:
            column_id: ID колонки.
            current_user: Текущий пользователь.
            pagination: Параметры пагинации.

        Returns:
            Tuple[List[KanbanCardDataSchema], int]: Список карточек и общее количество.

        Raises:
            KanbanColumnNotFoundError: Если колонка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет доступа к канбан-доске.
        """
        # Получаем колонку
        column = await self.data_manager.get_column(column_id)
        if not column:
            raise KanbanColumnNotFoundError(column_id)

        # Проверяем доступ к канбан-доске
        await self._check_board_access(column.board_id, current_user.id)

        self.logger.info(
            "Пользователь %s (ID: %s) запросил список карточек в колонке %s",
            current_user.username,
            current_user.id,
            column_id,
        )

        return await self.data_manager.get_cards(
            column_id=column_id, pagination=pagination
        )

    async def get_card(
        self, card_id: int, current_user: CurrentUserSchema
    ) -> KanbanCardResponseSchema:
        """
        Получает карточку канбан-доски по ID.

        Args:
            card_id: ID карточки.
            current_user: Текущий пользователь.

        Returns:
            KanbanCardResponseSchema: Данные карточки.

        Raises:
            KanbanCardNotFoundError: Если карточка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет доступа к канбан-доске.
        """
        # Получаем карточку
        card = await self.data_manager.get_card(card_id)
        if not card:
            raise KanbanCardNotFoundError(card_id)

        # Получаем колонку
        column = await self.data_manager.get_column(card.column_id)

        # Проверяем доступ к канбан-доске
        await self._check_board_access(column.board_id, current_user.id)

        self.logger.info(
            "Пользователь %s (ID: %s) получил карточку %s",
            current_user.username,
            current_user.id,
            card_id,
        )

        return KanbanCardResponseSchema(data=KanbanCardDataSchema.model_validate(card))

    async def update_card(
        self,
        card_id: int,
        card_data: UpdateKanbanCardSchema,
        current_user: CurrentUserSchema,
    ) -> KanbanCardUpdateResponseSchema:
        """
        Обновляет карточку канбан-доски.

        Args:
            card_id: ID карточки.
            card_data: Данные для обновления карточки.
            current_user: Текущий пользователь.

        Returns:
            KanbanCardUpdateResponseSchema: Данные обновленной карточки.

        Raises:
            KanbanCardNotFoundError: Если карточка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на редактирование доски.
        """
        # Получаем карточку
        card = await self.data_manager.get_card(card_id)
        if not card:
            raise KanbanCardNotFoundError(card_id)

        # Получаем колонку и доску
        column = await self.data_manager.get_column(card.column_id)
        board = await self.data_manager.get_board(column.board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board.id, "У вас нет прав на редактирование канбан-доски"
            )

        # Обновляем карточку
        updated_card = await self.data_manager.update_card(card_id, card_data)

        self.logger.info(
            "Пользователь %s (ID: %s) обновил карточку %s",
            current_user.username,
            current_user.id,
            card_id,
        )

        return KanbanCardUpdateResponseSchema(data=updated_card)

    async def delete_card(
        self, card_id: int, current_user: CurrentUserSchema
    ) -> KanbanCardDeleteResponseSchema:
        """
        Удаляет карточку канбан-доски.

        Args:
            card_id: ID карточки.
            current_user: Текущий пользователь.

        Returns:
            KanbanCardDeleteResponseSchema: Сообщение об успешном удалении.

        Raises:
            KanbanCardNotFoundError: Если карточка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на редактирование доски.
        """
        # Получаем карточку
        card = await self.data_manager.get_card(card_id)
        if not card:
            raise KanbanCardNotFoundError(card_id)

        # Получаем колонку и доску
        column = await self.data_manager.get_column(card.column_id)
        board = await self.data_manager.get_board(column.board_id)

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board.id, "У вас нет прав на редактирование канбан-доски"
            )

        # Удаляем карточку
        await self.data_manager.delete_card(card_id)

        self.logger.info(
            "Пользователь %s (ID: %s) удалил карточку %s",
            current_user.username,
            current_user.id,
            card_id,
        )

        return KanbanCardDeleteResponseSchema()

    async def move_card(
        self,
        card_id: int,
        move_data: MoveKanbanCardSchema,
        current_user: CurrentUserSchema,
    ) -> KanbanCardMoveResponseSchema:
        """
        Перемещает карточку между колонками или изменяет её порядок.

        Args:
            card_id: ID карточки.
            move_data: Данные для перемещения карточки.
            current_user: Текущий пользователь.

        Returns:
            KanbanCardMoveResponseSchema: Данные перемещенной карточки.

        Raises:
            KanbanCardNotFoundError: Если карточка не найдена.
            KanbanColumnNotFoundError: Если целевая колонка не найдена.
            KanbanBoardAccessDeniedError: Если у пользователя нет прав на редактирование доски.
        """
        # Получаем карточку
        card = await self.data_manager.get_card(card_id)
        if not card:
            raise KanbanCardNotFoundError(card_id)

        # Получаем исходную колонку и доску
        source_column = await self.data_manager.get_column(card.column_id)
        board = await self.data_manager.get_board(source_column.board_id)

        # Если указана целевая колонка, проверяем её существование
        if move_data.target_column_id is not None:
            target_column = await self.data_manager.get_column(
                move_data.target_column_id
            )
            if not target_column:
                raise KanbanColumnNotFoundError(move_data.target_column_id)

            # Проверяем, что целевая колонка принадлежит той же доске
            if target_column.board_id != board.id:
                raise KanbanColumnNotFoundError(
                    move_data.target_column_id,
                    "Целевая колонка должна принадлежать той же канбан-доске",
                )

        # Проверяем права на управление рабочим пространством
        can_manage = await self.workspace_data_manager.can_user_manage_workspace(
            board.workspace_id, current_user.id, WorkspaceRole.EDITOR
        )
        if not can_manage:
            raise KanbanBoardAccessDeniedError(
                board.id, "У вас нет прав на редактирование канбан-доски"
            )

        # Перемещаем карточку
        moved_card = await self.data_manager.move_card(
            card_id=card_id,
            target_column_id=move_data.target_column_id,
            new_order=move_data.new_order,
        )

        self.logger.info(
            "Пользователь %s (ID: %s) переместил карточку %s в колонку %s с порядком %s",
            current_user.username,
            current_user.id,
            card_id,
            move_data.target_column_id,
            move_data.new_order,
        )

        return KanbanCardMoveResponseSchema(data=moved_card)
