import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_validator

from app.models.v1.modules.work_permits import WorkerRole, WorkPermitStatus
from app.schemas.v1.base import BaseRequestSchema


class CreateParticipantSchema(BaseRequestSchema):
    """
    Схема создания участника наряда-допуска.

    Используется для добавления участника в наряд-допуск
    с указанием его роли в выполнении работ.

    Attributes:
        user_id: Идентификатор пользователя в системе
        role: Роль участника в данном наряде-допуске
    """
    user_id: uuid.UUID = Field(
        ...,
        description="Идентификатор пользователя в системе"
    )
    role: WorkerRole = Field(
        ...,
        description="Роль участника в наряде-допуске"
    )


class CreatePreparationMeasureSchema(BaseRequestSchema):
    """
    Схема создания мероприятия по подготовке рабочего места.

    Используется для добавления технического мероприятия
    по обеспечению безопасности работ.

    Attributes:
        electrical_installation: Наименование электроустановки
        disconnection_grounding: Описание отключений и заземлений
        isolation_fencing: Описание изоляции и ограждений
        order_number: Порядковый номер мероприятия
    """
    electrical_installation: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Наименование электроустановки"
    )
    disconnection_grounding: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Что должно быть отключено и заземлено"
    )
    isolation_fencing: str = Field(
        default="Не требуется",
        max_length=500,
        description="Что должно быть изолировано или ограждено"
    )
    order_number: int = Field(
        default=1,
        ge=1,
        le=50,
        description="Порядковый номер мероприятия в списке"
    )


class CreateWorkPermitSchema(BaseRequestSchema):
    """
    Схема создания наряда-допуска.

    Используется для создания нового наряда-допуска на выполнение
    работ в электроустановках с полным набором участников и мероприятий.

    Attributes:
        organization: Наименование организации
        subdivision: Подразделение, выдающее наряд
        work_description: Описание выполняемых работ
        work_start_date: Дата и время начала работ
        work_end_date: Дата и время окончания работ
        special_instructions: Дополнительные указания по безопасности
        permit_issued_date: Дата и время выдачи наряда
        permit_issuer_id: Идентификатор выдавшего наряд
        status: Статус наряда-допуска
        participants: Список участников наряда
        preparation_measures: Список мероприятий по подготовке
        workspace_id: Идентификатор рабочего пространства
    """
    organization: str = Field(
        default="ПАО \"Северсталь\"",
        max_length=200,
        description="Наименование организации, выдающей наряд"
    )
    subdivision: str = Field(
        default="ППП ЛПЦ-1",
        max_length=200,
        description="Подразделение, в котором выполняются работы"
    )

    # Описание работ
    work_description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Подробное описание выполняемых работ"
    )

    # Временные рамки работ
    work_start_date: datetime = Field(
        ...,
        description="Дата и время начала выполнения работ"
    )
    work_end_date: datetime = Field(
        ...,
        description="Дата и время окончания работ"
    )

    # Дополнительные указания
    special_instructions: Optional[str] = Field(
        None,
        max_length=2000,
        description="Дополнительные указания по технике безопасности"
    )

    # Информация о выдаче наряда
    permit_issued_date: datetime = Field(
        ...,
        description="Дата и время выдачи наряда-допуска"
    )
    permit_issuer_id: int = Field(
        ...,
        description="Идентификатор пользователя, выдавшего наряд"
    )

    # Статус наряда
    status: WorkPermitStatus = Field(
        default=WorkPermitStatus.DRAFT,
        description="Текущий статус наряда-допуска"
    )

    # Участники и мероприятия
    participants: List[CreateParticipantSchema] = Field(
        default_factory=list,
        max_items=20,
        description="Список участников наряда с их ролями"
    )
    preparation_measures: List[CreatePreparationMeasureSchema] = Field(
        default_factory=list,
        max_items=50,
        description="Список мероприятий по подготовке рабочих мест"
    )

    workspace_id: Optional[int] = Field(
        None,
        description="Идентификатор рабочего пространства"
    )

    @field_validator('work_end_date')
    @classmethod
    def validate_end_date(cls, v, values):
        """Проверяет, что дата окончания позже даты начала работ."""
        if 'work_start_date' in values and v <= values['work_start_date']:
            raise ValueError('Дата окончания должна быть позже даты начала')
        return v

    @field_validator('participants')
    @classmethod
    def validate_participants(cls, v):
        """Проверяет наличие обязательных ролей участников."""
        if len(v) < 1:
            raise ValueError('Должен быть указан хотя бы один участник')

        # Проверяем наличие производителя работ
        has_producer = any(p.role == WorkerRole.WORK_PRODUCER for p in v)
        if not has_producer:
            raise ValueError('Должен быть указан производитель работ')

        # Проверяем наличие допускающего
        has_issuer = any(p.role == WorkerRole.PERMIT_ISSUER for p in v)
        if not has_issuer:
            raise ValueError('Должен быть указан допускающий')

        return v


class UpdateWorkPermitSchema(BaseRequestSchema):
    """
    Схема обновления наряда-допуска.

    Используется для частичного обновления существующего наряда-допуска.
    Все поля опциональны для возможности выборочного изменения данных.

    Attributes:
        organization: Наименование организации
        subdivision: Подразделение
        work_description: Описание работ
        work_start_date: Дата начала работ
        work_end_date: Дата окончания работ
        special_instructions: Дополнительные указания
        permit_issued_date: Дата выдачи наряда
        permit_issuer_id: Идентификатор выдавшего наряд
        status: Статус наряда
        participants: Список участников
        preparation_measures: Список мероприятий
    """
    organization: Optional[str] = Field(
        None,
        max_length=200,
        description="Наименование организации"
    )
    subdivision: Optional[str] = Field(
        None,
        max_length=200,
        description="Подразделение"
    )

    work_description: Optional[str] = Field(
        None,
        min_length=10,
        max_length=2000,
        description="Описание выполняемых работ"
    )
    work_start_date: Optional[datetime] = Field(
        None,
        description="Дата и время начала работ"
    )
    work_end_date: Optional[datetime] = Field(
        None,
        description="Дата и время окончания работ"
    )
    special_instructions: Optional[str] = Field(
        None,
        max_length=2000,
        description="Дополнительные указания по безопасности"
    )

    permit_issued_date: Optional[datetime] = Field(
        None,
        description="Дата и время выдачи наряда"
    )
    permit_issuer_id: Optional[int] = Field(
        None,
        description="Идентификатор выдавшего наряд"
    )
    status: Optional[WorkPermitStatus] = Field(
        None,
        description="Статус наряда-допуска"
    )

    participants: Optional[List[CreateParticipantSchema]] = Field(
        None,
        description="Список участников наряда"
    )
    preparation_measures: Optional[List[CreatePreparationMeasureSchema]] = Field(
        None,
        description="Список мероприятий по подготовке"
    )


class CreateSubdivisionSchema(BaseRequestSchema):
    """
    Схема создания подразделения.

    Используется для добавления нового подразделения в справочник
    организационной структуры предприятия.

    Attributes:
        name: Наименование подразделения
        code: Уникальный код подразделения
        description: Описание функций подразделения
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Наименование подразделения"
    )
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Уникальный код подразделения"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание функций и назначения подразделения"
    )


class CreateProfessionSchema(BaseRequestSchema):
    """
    Схема создания профессии.

    Используется для добавления новой профессии или должности
    в справочник квалификаций персонала.

    Attributes:
        name: Наименование профессии
        code: Уникальный код профессии
        description: Описание обязанностей профессии
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Наименование профессии или должности"
    )
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Уникальный код профессии"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание обязанностей и требований к профессии"
    )
