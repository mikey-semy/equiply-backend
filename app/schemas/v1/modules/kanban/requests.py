from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.v1.base import BaseRequestSchema


class CreateKanbanBoardSchema(BaseRequestSchema):
    """
    Схема создания канбан-доски.

    Attributes:
        name (str): Название канбан-доски
        description (Optional[str]): Описание канбан-доски
        display_settings (Dict[str, Any]): Настройки отображения доски
        template_id (Optional[int]): ID шаблона модуля

        Examples:
        ```python
        # Базовое создание доски
        board_data = CreateKanbanBoardSchema(
            name="Проект Alpha",
            description="Канбан-доска для управления задачами проекта Alpha"
        )

        # Создание доски с настройками отображения
        board_data = CreateKanbanBoardSchema(
            name="Разработка приложения",
            description="Процесс разработки мобильного приложения",
            display_settings={
                "theme": "dark",
                "columnWidth": 280,
                "showTaskCount": True,
                "groupBy": "assignee",
                "sortBy": {"field": "priority", "direction": "desc"},
                "columnColors": {
                    "todo": "#e0f7fa",
                    "in_progress": "#e8f5e9",
                    "done": "#f3e5f5"
                }
            }
        )

        # Создание доски на основе шаблона
        board_data = CreateKanbanBoardSchema(
            name="Sprint 12",
            template_id=3  # Шаблон Agile Sprint
        )

        # Полный пример
        board_data = CreateKanbanBoardSchema(
            name="Поддержка клиентов",
            description="Канбан для отслеживания запросов клиентов",
            display_settings={
                "theme": "light",
                "columnWidth": 300,
                "swimlanes": True,
                "showDueDate": True,
                "defaultLabels": ["urgent", "feature", "bug"]
            },
            template_id=4  # Шаблон "Поддержка клиентов"
        )
        ```
    """

    name: str = Field(
        ..., min_length=1, max_length=255, description="Название канбан-доски"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Описание канбан-доски"
    )
    display_settings: Dict[str, Any] = Field(
        {},
        description="Настройки отображения доски",
        examples=[
            {"theme": "dark", "columnWidth": 280, "showTaskCount": True},
            {
                "theme": "light",
                "columnColors": {"todo": "#e0f7fa", "in_progress": "#e8f5e9"},
                "groupBy": "assignee",
            },
        ],
    )
    template_id: Optional[int] = Field(
        None,
        description="ID шаблона модуля, например: 1 - Базовый шаблон, 2 - Разработка ПО, 3 - Agile Sprint, 4 - Поддержка клиентов",
        examples=[1, 2, 3, 4],
    )


class UpdateKanbanBoardSchema(BaseRequestSchema):
    """
    Схема обновления канбан-доски.

    Attributes:
        name (Optional[str]): Новое название канбан-доски
        description (Optional[str]): Новое описание канбан-доски
        display_settings (Optional[Dict[str, Any]]): Новые настройки отображения доски
    """

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Новое название канбан-доски"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Новое описание канбан-доски"
    )
    display_settings: Optional[Dict[str, Any]] = Field(
        None, description="Новые настройки отображения доски"
    )


class CreateKanbanColumnSchema(BaseRequestSchema):
    """
    Схема создания колонки канбан-доски.

    Attributes:
        name (str): Название колонки
        order (int): Порядок колонки на доске
        wip_limit (Optional[int]): Лимит работы в процессе
        board_id (int): ID канбан-доски
    """

    name: str = Field(..., min_length=1, max_length=255, description="Название колонки")
    order: int = Field(..., description="Порядок колонки на доске")
    wip_limit: Optional[int] = Field(None, description="Лимит работы в процессе")
    board_id: int = Field(..., description="ID канбан-доски")


class UpdateKanbanColumnSchema(BaseRequestSchema):
    """
    Схема обновления колонки канбан-доски.

    Attributes:
        name (Optional[str]): Новое название колонки
        order (Optional[int]): Новый порядок колонки на доске
        wip_limit (Optional[int]): Новый лимит работы в процессе
    """

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Новое название колонки"
    )
    order: Optional[int] = Field(None, description="Новый порядок колонки на доске")
    wip_limit: Optional[int] = Field(None, description="Новый лимит работы в процессе")


class CreateKanbanCardSchema(BaseRequestSchema):
    """
    Схема создания карточки канбан-доски.

    Attributes:
        title (str): Заголовок карточки
        description (Optional[str]): Описание карточки
        order (int): Порядок карточки в колонке
        data (Dict[str, Any]): Дополнительные данные карточки
        column_id (int): ID колонки
    """

    title: str = Field(
        ..., min_length=1, max_length=255, description="Заголовок карточки"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Описание карточки"
    )
    order: int = Field(..., description="Порядок карточки в колонке")
    data: Dict[str, Any] = Field({}, description="Дополнительные данные карточки")
    column_id: int = Field(..., description="ID колонки")


class UpdateKanbanCardSchema(BaseRequestSchema):
    """
    Схема обновления карточки канбан-доски.

    Attributes:
        title (Optional[str]): Новый заголовок карточки
        description (Optional[str]): Новое описание карточки
        order (Optional[int]): Новый порядок карточки в колонке
        data (Optional[Dict[str, Any]]): Новые дополнительные данные карточки
        column_id (Optional[int]): Новый ID колонки (для перемещения)
    """

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Новый заголовок карточки"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Новое описание карточки"
    )
    order: Optional[int] = Field(None, description="Новый порядок карточки в колонке")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Новые дополнительные данные карточки"
    )
    column_id: Optional[int] = Field(
        None, description="Новый ID колонки (для перемещения)"
    )


class MoveKanbanCardSchema(BaseRequestSchema):
    """
    Схема перемещения карточки канбан-доски.

    Attributes:
        column_id (int): ID целевой колонки
        order (int): Новый порядок карточки в колонке
    """

    column_id: int = Field(..., description="ID целевой колонки")
    order: int = Field(..., description="Новый порядок карточки в колонке")


class ReorderKanbanColumnsSchema(BaseRequestSchema):
    """
    Схема изменения порядка колонок канбан-доски.

    Attributes:
        column_orders (List[Dict[str, int]]): Список с ID колонок и их новыми порядковыми номерами
    """

    column_orders: List[Dict[str, int]] = Field(
        ..., description="Список с ID колонок и их новыми порядковыми номерами"
    )


class UpdateKanbanBoardSettingsSchema(BaseRequestSchema):
    """
    Схема обновления настроек канбан-доски.

    Attributes:
        display_settings (Optional[Dict[str, Any]]): Настройки отображения доски
        automation_settings (Optional[Dict[str, Any]]): Настройки автоматизации
        notification_settings (Optional[Dict[str, Any]]): Настройки уведомлений
        access_settings (Optional[Dict[str, Any]]): Настройки доступа
    """

    display_settings: Optional[Dict[str, Any]] = None
    automation_settings: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    access_settings: Optional[Dict[str, Any]] = None
