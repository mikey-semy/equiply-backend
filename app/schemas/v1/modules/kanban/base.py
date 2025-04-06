from typing import Any, Dict, List, Optional

from pydantic import Field

from app.schemas.v1.base import BaseSchema, CommonBaseSchema

class KanbanCardDataSchema(BaseSchema):
    """
    Схема данных карточки канбан-доски.

    Attributes:
        title (str): Заголовок карточки
        description (Optional[str]): Описание карточки
        order (int): Порядок карточки в колонке
        data (Dict[str, Any]): Дополнительные данные карточки
        column_id (int): ID колонки
    """

    title: str
    description: Optional[str] = None
    order: int
    data: Dict[str, Any] = {}
    column_id: int


class KanbanColumnDataSchema(BaseSchema):
    """
    Схема данных колонки канбан-доски.

    Attributes:
        name (str): Название колонки
        order (int): Порядок колонки на доске
        wip_limit (Optional[int]): Лимит работы в процессе
        board_id (int): ID канбан-доски
        cards (List[KanbanCardDataSchema]): Карточки в колонке
    """

    name: str
    order: int
    wip_limit: Optional[int] = None
    board_id: int
    cards: List[KanbanCardDataSchema] = []


class KanbanBoardDataSchema(BaseSchema):
    """
    Схема данных канбан-доски.

    Attributes:
        name (str): Название канбан-доски
        description (Optional[str]): Описание канбан-доски
        display_settings (Dict[str, Any]): Настройки отображения доски
        workspace_id (int): ID рабочего пространства
        template_id (Optional[int]): ID шаблона модуля
        columns (List[KanbanColumnDataSchema]): Колонки доски
    """

    name: str
    description: Optional[str] = None
    display_settings: Dict[str, Any] = {}
    workspace_id: int
    template_id: Optional[int] = None
    columns: List[KanbanColumnDataSchema] = []


class KanbanBoardDetailDataSchema(KanbanBoardDataSchema):
    """
    Схема детальных данных канбан-доски.

    Attributes:
        columns_count (int): Количество колонок на доске
        cards_count (int): Общее количество карточек на доске
    """

    columns_count: int = 0
    cards_count: int = 0


class KanbanBoardSettingsDataSchema(CommonBaseSchema):
    """
    Схема данных настроек канбан-доски.
    
    Attributes:
        display_settings (Dict[str, Any]): Настройки отображения доски
        automation_settings (Dict[str, Any]): Настройки автоматизации
        notification_settings (Dict[str, Any]): Настройки уведомлений
        access_settings (Dict[str, Any]): Настройки доступа
    """
    
    display_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Настройки отображения доски",
        examples=[
            {
                "theme": "light",
                "columnWidth": 280,
                "showTaskCount": True,
                "columnColors": {
                    "todo": "#e0f7fa",
                    "in_progress": "#e8f5e9",
                    "done": "#f3e5f5"
                }
            }
        ]
    )
    automation_settings: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Настройки автоматизации канбан-доски",
        examples=[
            {
                "autoArchive": True,
                "autoAssign": False,
                "moveCompletedCards": True,
                "notifyOnDueDate": True
            }
        ]
    )
    notification_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Настройки уведомлений канбан-доски",
        examples=[
            {
                "emailNotifications": True,
                "pushNotifications": False,
                "notifyOnCardMove": True,
                "notifyOnComment": True
            }
        ]
    )
    access_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Настройки доступа к канбан-доске",
        examples=[
            {
                "allowPublicAccess": False,
                "allowExport": True,
                "allowGuestComments": False,
                "requireApproval": True
            }
        ]
    )

