from app.schemas.v1.base import BaseResponseSchema
from app.schemas.v1.modules.kanban.base import (KanbanBoardDataSchema,
                                                KanbanBoardDetailDataSchema,
                                                KanbanBoardSettingsDataSchema,
                                                KanbanCardDataSchema,
                                                KanbanColumnDataSchema)
from app.schemas.v1.pagination import Page


class KanbanBoardResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanBoardDataSchema): Данные канбан-доски
    """

    message: str = "Канбан-доска успешно получена"
    data: KanbanBoardDataSchema


class KanbanBoardDetailResponseSchema(BaseResponseSchema):
    """
    Схема ответа с детальными данными канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanBoardDetailDataSchema): Детальные данные канбан-доски
    """

    message: str = "Детальная информация о канбан-доске успешно получена"
    data: KanbanBoardDetailDataSchema


class KanbanBoardListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком канбан-досок.

    Attributes:
        message (str): Сообщение о результате операции
        data (Page[KanbanBoardDataSchema]): Список данных канбан-досок
    """

    message: str = "Список канбан-досок успешно получен"
    data: Page[KanbanBoardDataSchema]


class KanbanBoardCreateResponseSchema(KanbanBoardResponseSchema):
    """
    Схема ответа при создании канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanBoardDataSchema): Данные созданной канбан-доски
    """

    message: str = "Канбан-доска успешно создана"


class KanbanBoardUpdateResponseSchema(KanbanBoardResponseSchema):
    """
    Схема ответа при обновлении канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanBoardDataSchema): Данные обновленной канбан-доски
    """

    message: str = "Канбан-доска успешно обновлена"


class KanbanBoardDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Канбан-доска успешно удалена"


class KanbanColumnResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными колонки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanColumnDataSchema): Данные колонки канбан-доски
    """

    message: str = "Колонка канбан-доски успешно получена"
    data: KanbanColumnDataSchema


class KanbanColumnListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком колонок канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (Page[KanbanColumnDataSchema]): Список данных колонок канбан-доски
    """

    message: str = "Список колонок канбан-доски успешно получен"
    data: Page[KanbanColumnDataSchema]


class KanbanColumnCreateResponseSchema(KanbanColumnResponseSchema):
    """
    Схема ответа при создании колонки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanColumnDataSchema): Данные созданной колонки канбан-доски
    """

    message: str = "Колонка канбан-доски успешно создана"


class KanbanColumnUpdateResponseSchema(KanbanColumnResponseSchema):
    """
    Схема ответа при обновлении колонки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanColumnDataSchema): Данные обновленной колонки канбан-доски
    """

    message: str = "Колонка канбан-доски успешно обновлена"


class KanbanColumnDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении колонки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Колонка канбан-доски успешно удалена"


class KanbanColumnReorderResponseSchema(BaseResponseSchema):
    """
    Схема ответа при изменении порядка колонок канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Порядок колонок канбан-доски успешно изменен"


class KanbanCardResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными карточки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanCardDataSchema): Данные карточки канбан-доски
    """

    message: str = "Карточка канбан-доски успешно получена"
    data: KanbanCardDataSchema


class KanbanCardListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком карточек канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (Page[KanbanCardDataSchema]): Список данных карточек канбан-доски
    """

    message: str = "Список карточек канбан-доски успешно получен"
    data: Page[KanbanCardDataSchema]


class KanbanCardCreateResponseSchema(KanbanCardResponseSchema):
    """
    Схема ответа при создании карточки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanCardDataSchema): Данные созданной карточки канбан-доски
    """

    message: str = "Карточка канбан-доски успешно создана"


class KanbanCardUpdateResponseSchema(KanbanCardResponseSchema):
    """
    Схема ответа при обновлении карточки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanCardDataSchema): Данные обновленной карточки канбан-доски
    """

    message: str = "Карточка канбан-доски успешно обновлена"


class KanbanCardDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении карточки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Карточка канбан-доски успешно удалена"


class KanbanCardMoveResponseSchema(KanbanCardResponseSchema):
    """
    Схема ответа при перемещении карточки канбан-доски.

    Attributes:
        message (str): Сообщение о результате операции
        data (KanbanCardDataSchema): Данные перемещенной карточки канбан-доски
    """

    message: str = "Карточка канбан-доски успешно перемещена"


class KanbanBoardSettingsResponseSchema(BaseResponseSchema):
    """
    Схема ответа с настройками канбан-доски.

    Attributes:
        data (KanbanBoardSettingsDataSchema): Данные настроек канбан-доски
        message (str): Сообщение о результате операции
    """

    data: KanbanBoardSettingsDataSchema
    message: str = "Настройки канбан-доски получены"


class KanbanBoardSettingsUpdateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при обновлении настроек канбан-доски.

    Attributes:
        data (KanbanBoardSettingsDataSchema): Обновленные настройки канбан-доски
        message (str): Сообщение о результате операции
    """

    data: KanbanBoardSettingsDataSchema
    message: str = "Настройки канбан-доски обновлены"


class KanbanDefaultSettingsResponseSchema(BaseResponseSchema):
    """
    Схема ответа с настройками канбан-доски по умолчанию.

    Attributes:
        data (KanbanBoardSettingsDataSchema): Данные настроек по умолчанию
        message (str): Сообщение о результате операции
    """

    data: KanbanBoardSettingsDataSchema
    message: str = "Настройки канбан-доски по умолчанию получены"
