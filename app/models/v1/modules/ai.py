"""
Модуль, содержащий модель настроек пользователя.

Модель предназначена для хранения пользовательских настроек,
включая предпочитаемую модель AI для использования в чате.
"""

from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel
from app.models.v1 import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.v1.users import UserModel


class ModelType(str, Enum):
    YANDEX_GPT_LITE = "yandexgpt-lite"
    YANDEX_GPT_PRO = "yandexgpt"
    YANDEX_GPT_PRO_32K = "yandexgpt-32k"
    LLAMA_8B = "llama-lite"
    LLAMA_70B = "llama"
    CUSTOM = "custom"


class AISettingsModel(BaseModel):
    """
    Модель для хранения настроек пользователя.

    Attributes:
        user_id (int): ID пользователя, которому принадлежат настройки.
        preferred_model (ModelType): Предпочитаемая модель AI.
        temperature (float): Настройка температуры для генерации.
        max_tokens (int): Максимальное количество токенов для генерации.

    Relationships:
        user (UserModel): Пользователь, которому принадлежат настройки.
    """

    __tablename__ = "ai_settings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    preferred_model: Mapped[ModelType] = mapped_column(default=ModelType.LLAMA_70B)
    temperature: Mapped[float] = mapped_column(default=0.6)
    max_tokens: Mapped[int] = mapped_column(default=2000)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="ai_settings")
