from typing import Dict, List, Optional

from pydantic import Field

from app.schemas.v1.base import BaseCommonResponseSchema, BaseResponseSchema

from .base import AIChatSchema, AISettingsSchema, MessageSchema


class AIChatResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными чата.

    Attributes:
        message (str): Сообщение о результате операции.
        data (AIChatSchema): Данные чата.
    """

    message: str = "Чат успешно получен"
    data: AIChatSchema


class AIChatsListResponseSchema(BaseResponseSchema):
    """
    Схема ответа со списком чатов.

    Attributes:
        message (str): Сообщение о результате операции.
        data (List[AIChatSchema]): Список чатов.
    """

    message: str = "Список чатов успешно получен"
    data: List[AIChatSchema]


class AIChatCreateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при создании чата.

    Attributes:
        message (str): Сообщение о результате операции.
        data (AIChatSchema): Данные созданного чата.
    """

    message: str = "Чат успешно создан"
    data: AIChatSchema


class AIChatUpdateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при обновлении чата.

    Attributes:
        message (str): Сообщение о результате операции.
        data (AIChatSchema): Данные обновленного чата.
    """

    message: str = "Чат успешно обновлен"
    data: AIChatSchema


class AIChatDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа при удалении чата.

    Attributes:
        message (str): Сообщение о результате операции.
        success (bool): Признак успешного выполнения операции.
    """

    message: str = "Чат успешно удален"
    success: bool = True


class AlternativeSchema(BaseResponseSchema):
    """
    Альтернативный ответ модели

    Attributes:
        message: Сообщение от модели
        status: Статус генерации
    """

    message: MessageSchema
    status: str


class UsageSchema(BaseCommonResponseSchema):
    """
    Статистика использования токенов

    Attributes:
        inputTextTokens: Количество токенов во входном тексте
        completionTokens: Количество токенов в ответе
        totalTokens: Общее количество токенов
    """

    inputTextTokens: str
    completionTokens: str
    totalTokens: str


class ResultSchema(BaseCommonResponseSchema):
    """
    Результат генерации

    Attributes:
        alternatives: Список альтернативных ответов
        usage: Статистика использования
        modelVersion: Версия модели
    """

    alternatives: List[AlternativeSchema]
    usage: UsageSchema
    modelVersion: str


class AIResponseSchema(BaseCommonResponseSchema):
    """
    Схема ответа AI чата

    Attributes:
        success: Флаг успешности запроса
        result: Результат генерации
    """

    success: bool = True
    result: ResultSchema
    message: Optional[str] = Field(default=None, exclude=True)


class AISettingsResponseSchema(BaseResponseSchema):
    """
    Схема ответа с настройками AI пользователя
    Attributes:
        message: Сообщение о результате операции
        data: Данные настроек AI пользователя
    """

    message: str = "Настройки AI успешно получены"
    data: AISettingsSchema


class AISettingsUpdateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при обновлении настроек AI пользователя
    Attributes:
        message: Сообщение о результате операции
        data: Обновленные данные настроек AI пользователя
    """

    message: str = "Настройки AI успешно обновлены"
    data: AISettingsSchema


class AIChatHistoryClearResponseSchema(BaseResponseSchema):
    """
    Схема ответа при очистке истории чата с AI
    Attributes:
        message: Сообщение о результате операции
        success: Признак успешного выполнения операции
    """

    message: str = "История чата успешно очищена"
    success: bool = True


class AIChatHistoryExportResponseSchema(BaseResponseSchema):
    """
    Схема ответа при экспорте истории чата с AI
    Attributes:
        message: Сообщение о результате операции
        data: Список сообщений в истории чата
    """

    message: str = "История чата успешно экспортирована"
    data: List[MessageSchema]


class SystemMessageResponseSchema(BaseResponseSchema):
    """
    Схема ответа с системным сообщением

    Attributes:
        message: Сообщение о результате операции
        data: Данные системного сообщения
    """

    message: str = "Системное сообщение получено успешно"
    data: str


class SystemMessageUpdateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при обновлении системного сообщения

    Attributes:
        message: Сообщение о результате операции
        data: Обновленные данные системного сообщения
    """

    message: str = "Системное сообщение обновлено успешно"
    data: str


class ModelUsageStatsSchema(BaseCommonResponseSchema):
    """
    Схема статистики использования конкретной модели

    Attributes:
        total_tokens: Общее количество использованных токенов
        total_cost: Общая стоимость использования в рублях
        usage_count: Количество использований модели
        average_tokens: Среднее количество токенов на запрос
    """

    total_tokens: int = 0
    total_cost: float = 0.0
    usage_count: int = 0
    average_tokens: float = 0.0


class ChatStatsDataSchema(BaseCommonResponseSchema):
    """
    Схема данных статистики по чатам

    Attributes:
        total_chats: Общее количество чатов
        active_chats: Количество активных чатов
        inactive_chats: Количество неактивных чатов
        total_messages: Общее количество сообщений
        total_tokens: Общее количество токенов
        total_cost: Общая стоимость использования в рублях
        models_usage: Статистика использования по моделям
        last_active_chat: Последний активный чат
    """

    total_chats: int = 0
    active_chats: int = 0
    inactive_chats: int = 0
    total_messages: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    models_usage: Dict[str, ModelUsageStatsSchema] = Field(default_factory=dict)
    last_active_chat: Optional[AIChatSchema] = None


class AIChatStatsResponseSchema(BaseResponseSchema):
    """
    Схема ответа с данными статистики чата

    Attributes:
        message: Сообщение о результате операции
        data: Данные статистики чата
    """

    message: str = "Статистика чата успешно получена"
    data: Optional[ChatStatsDataSchema] = None
