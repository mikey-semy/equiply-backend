"""
Модуль, содержащий модель настроек пользователя.

Модель предназначена для хранения пользовательских настроек,
включая предпочитаемую модель AI для использования в чате.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
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


class AIChatModel(BaseModel):
    """
    Модель для хранения метаданных чатов с AI.

    Attributes:
        user_id (int): ID пользователя, которому принадлежит чат.
        title (str): Название чата.
        description (str): Описание чата.
        chat_id (str): Уникальный идентификатор чата для хранения в Redis.
        last_message_at (datetime): Время последнего сообщения.
        is_active (bool): Флаг активности чата.
    """

    __tablename__ = "ai_chats"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(default="Новый чат")
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    chat_id: Mapped[str] = mapped_column(unique=True, index=True)
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="ai_chats")


class AISettingsModel(BaseModel):
    """
    Модель для хранения настроек пользователя.

    Attributes:
        user_id (int): ID пользователя, которому принадлежат настройки.
        preferred_model (ModelType): Предпочитаемая модель AI.
        temperature (float): Настройка температуры для генерации.
        max_tokens (int): Максимальное количество токенов для генерации.
        system_message (str): Системное сообщение для чата.

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
    system_message: Mapped[str] = mapped_column(
        default="Ты ассистент, помогающий пользователю.", nullable=True
    )

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="ai_settings")
