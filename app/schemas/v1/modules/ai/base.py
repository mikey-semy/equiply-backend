from enum import Enum

from app.models.v1.modules.ai import ModelType
from app.schemas.v1.base import BaseSchema, CommonBaseSchema


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ModelVersion(str, Enum):
    DEPRECATED = "deprecated"
    LATEST = "latest"
    RC = "rc"


class AISettingsSchema(BaseSchema):
    """
    Схема настроек пользователя для AI.

    Attributes:
        user_id (int): ID пользователя, которому принадлежат настройки.
        preferred_model (ModelType): Предпочитаемая модель AI.
        temperature (float): Настройка температуры для генерации.
        max_tokens (int): Максимальное количество токенов для генерации.
    """

    user_id: int
    preferred_model: ModelType = ModelType.LLAMA_70B
    temperature: float = 0.6
    max_tokens: int = 2000


class ModelPricing(Enum):
    """
    Цены и юниты для разных моделей и режимов
    """

    YANDEX_GPT_LITE_SYNC = (1, 0.20)  # (юниты, цена в рублях за 1000 токенов)
    YANDEX_GPT_LITE_ASYNC = (0.5, 0.10)
    YANDEX_GPT_PRO_SYNC = (6, 1.20)
    YANDEX_GPT_PRO_ASYNC = (3, 0.60)
    DATASPHERE_SYNC = (6, 1.20)
    DATASPHERE_ASYNC = (3, 0.60)
    LLAMA_8B_SYNC = (1, 0.20)
    LLAMA_8B_ASYNC = (0.5, 0.10)
    LLAMA_70B_SYNC = (6, 1.20)
    LLAMA_70B_ASYNC = (3, 0.60)


class MessageSchema(CommonBaseSchema):
    """
    Схема сообщения для чата с AI

    Attributes:
        role: Роль отправителя сообщения
        text: Текст сообщения
    """

    role: MessageRole
    text: str
