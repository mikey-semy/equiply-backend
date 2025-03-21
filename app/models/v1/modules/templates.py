from typing import Any, Dict, Optional

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.users import UserModel


class ModuleTemplateModel(BaseModel):
    """
    Модель шаблона модуля (таблицы или списка)

    Attributes:
        name (str): Название шаблона
        description (str): Описание шаблона
        module_type (str): Тип модуля (table, list)
        schema (Dict[str, Any]): Схема модуля
        is_public (bool): Доступен ли шаблон всем пользователям
        creator_id (int): ID создателя шаблона

    Relationships:
        creator (UserModel): Создатель шаблона
    """

    __tablename__ = "module_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    module_type: Mapped[str] = mapped_column(String(50), nullable=False)
    schema: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_public: Mapped[bool] = mapped_column(default=False)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Связи
    creator: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="created_templates"
    )
