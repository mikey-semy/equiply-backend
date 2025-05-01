from typing import List, Optional

from pydantic import Field
from app.core.settings import settings
from app.models.v1.modules.ai import ModelType
from app.schemas.v1.base import BaseRequestSchema

from .base import MessageSchema

class AIChatCreateSchema(BaseRequestSchema):
    """
    Схема для создания нового чата с AI.

    Attributes:
        title (str): Название чата.
        description (Optional[str]): Описание чата.
    """
    title: str = "Новый чат"
    description: Optional[str] = None


class AIChatUpdateSchema(BaseRequestSchema):
    """
    Схема для обновления чата с AI.

    Attributes:
        title (Optional[str]): Новое название чата.
        description (Optional[str]): Новое описание чата.
        is_active (Optional[bool]): Новый статус активности.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AISettingsUpdateSchema(BaseRequestSchema):
    """
    Схема для обновления настроек AI пользователя.

    Attributes:
        preferred_model (Optional[ModelType]): Предпочитаемая модель AI.
        temperature (Optional[float]): Настройка температуры для генерации.
        max_tokens (Optional[int]): Максимальное количество токенов для генерации.
        system_message (Optional[str]): Системное сообщение для чата.
    """
    preferred_model: Optional[ModelType] = ModelType.LLAMA_70B
    temperature: Optional[float] = settings.YANDEX_TEMPERATURE
    max_tokens: Optional[int] = settings.YANDEX_MAX_TOKENS
    system_message: Optional[str] = settings.YANDEX_PRE_INSTRUCTIONS

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
    maxTokens: int = Field(default=2000)
    reasoningOptions: ReasoningOptionsSchema = Field(
        default_factory=ReasoningOptionsSchema
    )


class AIRequestSchema(BaseRequestSchema):
    """
    Схема запроса к AI чату

    Attributes:
        modelUri: URI модели
        completionOptions: Настройки генерации
        messages: Список сообщений
    """

    modelUri: str
    completionOptions: CompletionOptionsSchema = Field(
        default_factory=CompletionOptionsSchema
    )
    messages: List[MessageSchema]


class SystemMessageUpdateRequestSchema(BaseRequestSchema):
    """
    Схема для обновления системного сообщения

    Attributes:
        message: Новый текст системного сообщения
    """

    message: str
