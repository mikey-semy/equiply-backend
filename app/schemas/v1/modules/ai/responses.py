from typing import List, Optional

from pydantic import Field

from app.schemas.v1.base import BaseResponseSchema, BaseCommonResponseSchema

from .base import AISettingsSchema, MessageSchema


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
