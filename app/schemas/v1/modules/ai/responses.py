from typing import List, Optional

from pydantic import Field

from app.schemas.v1.base import BaseResponseSchema

from .base import MessageSchema


class AlternativeSchema(BaseResponseSchema):
    """
    Альтернативный ответ модели

    Attributes:
        message: Сообщение от модели
        status: Статус генерации
    """

    message: MessageSchema
    status: str


class UsageSchema(BaseResponseSchema):
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


class ResultSchema(BaseResponseSchema):
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


class AIResponseSchema(BaseResponseSchema):
    """
    Схема ответа AI чата

    Attributes:
        success: Флаг успешности запроса
        result: Результат генерации
    """

    success: bool = True
    result: ResultSchema
    message: Optional[str] = Field(default=None, exclude=True)
