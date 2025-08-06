import uuid
from enum import Enum
from typing import List, Optional
from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.v1.base import BaseModel
from app.models.v1 import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.v1.users import UserModel
    from app.models.v1.workspaces import WorkspaceModel


class ElectricalSafetyGroup(str, Enum):
    """
    Группы по электробезопасности.

    Определяет уровень квалификации персонала для работы с электроустановками.

    Attributes:
        GROUP_I: I группа по электробезопасности - неэлектротехнический персонал
        GROUP_II: II группа по электробезопасности - электротехнический персонал
        GROUP_III: III группа по электробезопасности - электротехнический персонал
        GROUP_IV: IV группа по электробезопасности - электротехнический персонал
        GROUP_V: V группа по электробезопасности - электротехнический персонал
    """
    GROUP_I = "I"
    GROUP_II = "II"
    GROUP_III = "III"
    GROUP_IV = "IV"
    GROUP_V = "V"


class WorkerRole(str, Enum):
    """
    Роли участников в конкретном наряде-допуске.

    Определяет функции и ответственность каждого участника при выполнении работ.

    Attributes:
        RESPONSIBLE_SUPERVISOR: Ответственный руководитель работ - отвечает за безопасность
        PERMIT_ISSUER: Допускающий (оперативный персонал) - выдает наряд-допуск
        WORK_PRODUCER: Производитель работ - руководит бригадой на месте работ
        OBSERVER: Наблюдающий - контролирует безопасность при работах под напряжением
        BRIGADE_MEMBER: Член бригады - выполняет работы под руководством производителя
    """
    RESPONSIBLE_SUPERVISOR = "responsible_supervisor"
    PERMIT_ISSUER = "permit_issuer"
    WORK_PRODUCER = "work_producer"
    OBSERVER = "observer"
    BRIGADE_MEMBER = "brigade_member"

class WorkPermitStatus(str, Enum):
    """
    Статусы наряда-допуска.

    Отражает текущее состояние наряда-допуска в процессе его жизненного цикла.

    Attributes:
        DRAFT: Черновик наряда - наряд создан, но еще не выдан
        ISSUED: Наряд выдан - наряд оформлен и передан для выполнения работ
        EXTENDED: Наряд продлен - срок действия наряда продлен
        COMPLETED: Работы завершены - все работы по наряду выполнены
        CANCELLED: Наряд отменен - наряд аннулирован до завершения работ
    """
    DRAFT = "draft"
    ISSUED = "issued"
    EXTENDED = "extended"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkPermitParticipantModel(BaseModel):
    """
    Модель участника наряда-допуска с его ролью.

    Связывает пользователя с нарядом-допуском и определяет его роль и ответственность
    в данном конкретном наряде.

    Attributes:
        work_permit_id: Идентификатор наряда-допуска
        user_id: Идентификатор пользователя-участника
        role: Роль участника в данном наряде (производитель, член бригады и т.д.)

    Relationships:
        work_permit: Наряд-допуск, к которому относится участник
        user: Пользователь-участник наряда
    """
    __tablename__ = "work_permit_participants"

    work_permit_id: Mapped[int] = mapped_column(ForeignKey("work_permits.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    role: Mapped[WorkerRole] = mapped_column()

    # Связи с другими таблицами
    work_permit: Mapped["WorkPermitModel"] = relationship(
        "WorkPermitModel", back_populates="participants"
    )
    user: Mapped["UserModel"] = relationship("UserModel")


class WorkPermitPreparationMeasureModel(BaseModel):
    """
    Модель мероприятий по подготовке рабочих мест.

    Описывает конкретные технические мероприятия, которые необходимо выполнить
    для обеспечения безопасности работ в электроустановках.

    Attributes:
        work_permit_id: Идентификатор наряда-допуска
        electrical_installation: Наименование электроустановки, в которой выполняются работы
        disconnection_grounding: Описание отключений и заземлений
        isolation_fencing: Описание изоляции и ограждений
        order_number: Порядковый номер мероприятия в списке

    Relationships:
        work_permit: Наряд-допуск, к которому относится мероприятие
    """
    __tablename__ = "work_permit_preparation_measures"

    work_permit_id: Mapped[int] = mapped_column(ForeignKey("work_permits.id"))
    electrical_installation: Mapped[str]
    disconnection_grounding: Mapped[str]
    isolation_fencing: Mapped[str] = mapped_column(default="Не требуется")
    order_number: Mapped[int] = mapped_column(default=1)

    # Связь с нарядом-допуском
    work_permit: Mapped["WorkPermitModel"] = relationship(
        "WorkPermitModel", back_populates="preparation_measures"
    )


class WorkPermitModel(BaseModel):
    """
    Модель наряда-допуска.

    Основная модель для хранения информации о наряде-допуске на выполнение работ
    в электроустановках согласно требованиям ПОТ РМ-016-2001. #TODO: проверить

    Attributes:
        organization: Название организации, выдающей наряд
        subdivision: Подразделение, в котором выполняются работы
        work_description: Подробное описание выполняемых работ
        work_start_date: Дата и время начала выполнения работ
        work_end_date: Дата и время окончания работ
        special_instructions: Дополнительные указания по технике безопасности
        permit_issued_date: Дата и время выдачи наряда-допуска
        permit_issuer_id: Идентификатор пользователя, выдавшего наряд
        status: Текущий статус наряда-допуска
        workspace_id: Идентификатор рабочего пространства (опционально)

    Relationships:
        permit_issuer: Пользователь, выдавший наряд-допуск
        workspace: Рабочее пространство, к которому относится наряд
        participants: Список участников наряда с указанием их ролей
        preparation_measures: Мероприятия по подготовке рабочих мест
    """
    __tablename__ = "work_permits"

    # Основная информация об организации
    organization: Mapped[str] = mapped_column(default="ПАО \"Северсталь\"")
    subdivision: Mapped[str] = mapped_column(default="ППП ЛПЦ-1")

    # Описание выполняемых работ
    work_description: Mapped[str] = mapped_column(Text)

    # Временные рамки выполнения работ
    work_start_date: Mapped[datetime]
    work_end_date: Mapped[datetime]

    # Дополнительные указания по безопасности
    special_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Информация о выдаче наряда
    permit_issued_date: Mapped[datetime]
    permit_issuer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    # Текущий статус наряда
    status: Mapped[WorkPermitStatus] = mapped_column(default=WorkPermitStatus.DRAFT)

    # Связь с рабочим пространством
    workspace_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workspaces.id"), nullable=True
    )

    # Связи с другими таблицами
    permit_issuer: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[permit_issuer_id]
    )
    workspace: Mapped[Optional["WorkspaceModel"]] = relationship("WorkspaceModel")

    # Участники наряда с их ролями
    participants: Mapped[List["WorkPermitParticipantModel"]] = relationship(
        "WorkPermitParticipantModel", back_populates="work_permit", cascade="all, delete-orphan"
    )

    # Мероприятия по подготовке рабочих мест
    preparation_measures: Mapped[List["WorkPermitPreparationMeasureModel"]] = relationship(
        "WorkPermitPreparationMeasureModel", back_populates="work_permit", cascade="all, delete-orphan"
    )
