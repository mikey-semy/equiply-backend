from typing import List, Optional

from pydantic import Field

from app.schemas.v1.base import BaseRequestSchema
from app.models.v1.modules.ai import ModelType
from .base import MessageSchema

class AISettingsUpdateSchema(BaseRequestSchema):
    """
    Схема для обновления настроек AI пользователя.

    Attributes:
        preferred_model (Optional[ModelType]): Предпочитаемая модель AI.
        temperature (Optional[float]): Настройка температуры для генерации.
        max_tokens (Optional[int]): Максимальное количество токенов для генерации.
    """
    preferred_model: Optional[ModelType] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class ReasoningOptionsSchema(BaseRequestSchema):
    """
    Настройки рассуждений модели

    Attributes:
        mode: Режим рассуждений (DISABLED/ENABLED)
    """

    mode: str = "DISABLED"


class CompletionOptionsSchema(BaseRequestSchema):
    """
    Настройки генерации ответа

    Attributes:
        stream: Потоковая генерация
        temperature: Температура генерации
        maxTokens: Максимальное количество токенов
        reasoningOptions: Настройки рассуждений
    """

    stream: bool = Field(default=False)
    temperature: float = Field(default=0.6)
    maxTokens: str = Field(default="2000")
    reasoningOptions: ReasoningOptionsSchema = Field(default_factory=ReasoningOptionsSchema)



class AIRequestSchema(BaseRequestSchema):
    """
    Схема запроса к AI чату

    Attributes:
        modelUri: URI модели
        completionOptions: Настройки генерации
        messages: Список сообщений
    """

    modelUri: str
    completionOptions: CompletionOptionsSchema = Field(default_factory=CompletionOptionsSchema)
    messages: List[MessageSchema]
