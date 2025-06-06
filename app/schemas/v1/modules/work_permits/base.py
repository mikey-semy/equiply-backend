from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.models.v1.modules.work_permits import (
    ElectricalSafetyGroup,
    WorkerRole,
    WorkPermitStatus
)
from app.schemas.v1.base import BaseSchema, CommonBaseSchema


class ParticipantSchema(BaseSchema):
    """
    Схема участника наряда-допуска.

    Содержит информацию об участнике работ с указанием его роли,
    квалификации и организационной принадлежности.

    Attributes:
        user_id: Идентификатор пользователя в системе
        username: Имя пользователя для отображения
        role: Роль участника в данном наряде-допуске
        electrical_safety_group: Группа по электробезопасности участника
        profession_name: Наименование профессии участника
        subdivision_name: Наименование подразделения участника
    """
    user_id: int
    username: str
    role: WorkerRole
    electrical_safety_group: Optional[ElectricalSafetyGroup] = None
    profession_name: Optional[str] = None
    subdivision_name: Optional[str] = None


class PreparationMeasureSchema(BaseSchema):
    """
    Схема мероприятия по подготовке рабочего места.

    Описывает технические мероприятия, необходимые для обеспечения
    безопасности работ в электроустановках.

    Attributes:
        electrical_installation: Наименование электроустановки
        disconnection_grounding: Описание отключений и заземлений
        isolation_fencing: Описание изоляции и ограждений
        order_number: Порядковый номер мероприятия
    """
    electrical_installation: str = Field(
        ...,
        description="Наименование электроустановки, в которой выполняются работы"
    )
    disconnection_grounding: str = Field(
        ...,
        description="Описание того, что должно быть отключено и заземлено"
    )
    isolation_fencing: str = Field(
        default="Не требуется",
        description="Описание того, что должно быть изолировано или ограждено"
    )
    order_number: int = Field(
        default=1,
        description="Порядковый номер мероприятия в списке"
    )


class WorkPermitSchema(CommonBaseSchema):
    """
    Базовая схема наряда-допуска.

    Содержит основную информацию о наряде-допуске на выполнение работ
    в электроустановках с указанием участников и мер безопасности.

    Attributes:
        organization: Наименование организации, выдающей наряд
        subdivision: Подразделение, в котором выполняются работы
        work_description: Подробное описание выполняемых работ
        work_start_date: Дата и время начала работ
        work_end_date: Дата и время окончания работ
        special_instructions: Дополнительные указания по безопасности
        permit_issued_date: Дата и время выдачи наряда
        permit_issuer_id: Идентификатор выдавшего наряд
        permit_issuer_name: Имя выдавшего наряд для отображения
        permit_issuer_profession: Профессия выдавшего наряд
        permit_issuer_group: Группа по электробезопасности выдавшего
        status: Текущий статус наряда-допуска
        participants: Список участников наряда с их ролями
        preparation_measures: Список мероприятий по подготовке
    """
    organization: str = "ПАО \"Северсталь\""
    subdivision: str = "ППП ЛПЦ-1"

    # Описание выполняемых работ
    work_description: str

    # Временные рамки работ
    work_start_date: datetime
    work_end_date: datetime

    # Дополнительные указания
    special_instructions: Optional[str] = None

    # Информация о выдаче наряда
    permit_issued_date: datetime
    permit_issuer_id: int
    permit_issuer_name: str
    permit_issuer_profession: Optional[str] = None
    permit_issuer_group: Optional[ElectricalSafetyGroup] = None

    # Статус наряда
    status: WorkPermitStatus

    # Участники и мероприятия
    participants: List[ParticipantSchema] = []
    preparation_measures: List[PreparationMeasureSchema] = []


class WorkPermitDetailSchema(WorkPermitSchema):
    """
    Детальная схема наряда-допуска.

    Расширенная версия базовой схемы с дополнительной информацией
    о привязке к рабочему пространству.

    Attributes:
        workspace_id: Идентификатор рабочего пространства
    """
    workspace_id: Optional[int] = None


class SubdivisionSchema(CommonBaseSchema):
    """
    Схема подразделения организации.

    Представляет структурное подразделение предприятия
    для организационной классификации сотрудников.

    Attributes:
        name: Наименование подразделения
        code: Уникальный код подразделения
        description: Описание функций подразделения
        is_active: Флаг активности подразделения
    """
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class ProfessionSchema(CommonBaseSchema):
    """
    Схема профессии/должности.

    Представляет профессию или должность сотрудника
    для квалификационной классификации персонала.

    Attributes:
        name: Наименование профессии
        code: Уникальный код профессии
        description: Описание обязанностей профессии
        is_active: Флаг активности профессии
    """
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class UserForSelectionSchema(CommonBaseSchema):
    """
    Схема пользователя для выбора в наряд-допуск.

    Упрощенная схема пользователя с информацией, необходимой
    для выбора участников при создании наряда-допуска.

    Attributes:
        username: Имя пользователя
        electrical_safety_group: Группа по электробезопасности
        profession_name: Наименование профессии
        subdivision_name: Наименование подразделения
        is_active: Флаг активности пользователя
    """
    username: str
    electrical_safety_group: Optional[ElectricalSafetyGroup] = None
    profession_name: Optional[str] = None
    subdivision_name: Optional[str] = None
    is_active: bool = True
