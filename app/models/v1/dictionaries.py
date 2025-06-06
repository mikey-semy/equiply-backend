from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.v1.base import BaseModel
from app.models.v1 import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.v1.users import UserModel


class SubdivisionModel(BaseModel):
    """
    Модель подразделения организации.

    Справочник структурных подразделений предприятия для категоризации
    сотрудников и определения их организационной принадлежности.

    Attributes:
        name: Полное наименование подразделения
        code: Уникальный код подразделения для внутреннего учета
        description: Подробное описание функций и назначения подразделения
        is_active: Флаг активности подразделения в системе

    Relationships:
        users: Список пользователей, относящихся к данному подразделению
    """
    __tablename__ = "subdivisions"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    code: Mapped[Optional[str]] = mapped_column(nullable=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Связи с другими таблицами
    users: Mapped[List["UserModel"]] = relationship(
        "UserModel", back_populates="subdivision_ref"
    )


class ProfessionModel(BaseModel):
    """
    Модель профессии/должности сотрудника.

    Справочник профессий и должностей для классификации персонала
    по их специализации и квалификации.

    Attributes:
        name: Наименование профессии или должности
        code: Уникальный код профессии для систематизации
        description: Описание обязанностей и требований к профессии
        is_active: Флаг активности профессии в справочнике

    Relationships:
        users: Список пользователей с данной профессией
    """
    __tablename__ = "professions"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    code: Mapped[Optional[str]] = mapped_column(nullable=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Связи с другими таблицами
    users: Mapped[List["UserModel"]] = relationship(
        "UserModel", back_populates="profession_ref"
    )
