from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.v1.access import ResourceType, PermissionType
from app.models.v1.users import UserRole
from app.schemas.v1.users import CurrentUserSchema
from app.schemas.v1.access import AccessPolicyCreateSchema
from app.services.v1.base import BaseService
from app.services.v1.access.service import AccessControlService

# Базовые политики для рабочих пространств
workspace_policies = [
    {
        "name": "Политика владельца рабочего пространства",
        "description": "Полный доступ к рабочему пространству",
        "resource_type": ResourceType.WORKSPACE,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value,
            PermissionType.DELETE.value,
            PermissionType.MANAGE.value,
            PermissionType.ADMIN.value
        ],
        "priority": 100,
        "is_active": True
    },
    {
        "name": "Политика администратора рабочего пространства",
        "description": "Управление рабочим пространством без права удаления",
        "resource_type": ResourceType.WORKSPACE,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value,
            PermissionType.MANAGE.value
        ],
        "priority": 90,
        "is_active": True
    },
    {
        "name": "Политика модератора рабочего пространства",
        "description": "Управление контентом рабочего пространства",
        "resource_type": ResourceType.WORKSPACE,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value,
            PermissionType.MANAGE.value
        ],
        "priority": 80,
        "is_active": True
    },
    {
        "name": "Политика редактора рабочего пространства",
        "description": "Редактирование контента рабочего пространства",
        "resource_type": ResourceType.WORKSPACE,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value
        ],
        "priority": 70,
        "is_active": True
    },
    {
        "name": "Политика просмотра рабочего пространства",
        "description": "Только просмотр рабочего пространства",
        "resource_type": ResourceType.WORKSPACE,
        "permissions": [
            PermissionType.READ.value
        ],
        "priority": 60,
        "is_active": True
    }
]

# Политики для таблиц
table_policies = [
    {
        "name": "Политика владельца таблицы",
        "description": "Полный доступ к таблице",
        "resource_type": ResourceType.TABLE,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value,
            PermissionType.DELETE.value,
            PermissionType.MANAGE.value
        ],
        "priority": 100,
        "is_active": True
    },
    {
        "name": "Политика редактора таблицы",
        "description": "Редактирование данных таблицы",
        "resource_type": ResourceType.TABLE,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value
        ],
        "priority": 80,
        "is_active": True
    },
    {
        "name": "Политика просмотра таблицы",
        "description": "Только просмотр таблицы",
        "resource_type": ResourceType.TABLE,
        "permissions": [
            PermissionType.READ.value
        ],
        "priority": 60,
        "is_active": True
    },
    {
        "name": "Политика временного доступа к таблице",
        "description": "Доступ к таблице только в рабочее время",
        "resource_type": ResourceType.TABLE,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value
        ],
        "conditions": {
            "time_range": {
                "start": "09:00",
                "end": "18:00"
            }
        },
        "priority": 70,
        "is_active": True
    }
]

# Политики для списков
list_policies = [
    {
        "name": "Политика владельца списка",
        "description": "Полный доступ к списку",
        "resource_type": ResourceType.LIST,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value,
            PermissionType.DELETE.value,
            PermissionType.MANAGE.value
        ],
        "priority": 100,
        "is_active": True
    },
    {
        "name": "Политика редактора списка",
        "description": "Редактирование элементов списка",
        "resource_type": ResourceType.LIST,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value
        ],
        "priority": 80,
        "is_active": True
    },
    {
        "name": "Политика просмотра списка",
        "description": "Только просмотр списка",
        "resource_type": ResourceType.LIST,
        "permissions": [
            PermissionType.READ.value
        ],
        "priority": 60,
        "is_active": True
    }
]

# Политики для канбан-досок
kanban_policies = [
    {
        "name": "Политика владельца канбан-доски",
        "description": "Полный доступ к канбан-доске",
        "resource_type": ResourceType.KANBAN,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value,
            PermissionType.DELETE.value,
            PermissionType.MANAGE.value
        ],
        "priority": 100,
        "is_active": True
    },
    {
        "name": "Политика редактора канбан-доски",
        "description": "Редактирование карточек и колонок",
        "resource_type": ResourceType.KANBAN,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value
        ],
        "priority": 80,
        "is_active": True
    },
    {
        "name": "Политика просмотра канбан-доски",
        "description": "Только просмотр канбан-доски",
        "resource_type": ResourceType.KANBAN,
        "permissions": [
            PermissionType.READ.value
        ],
        "priority": 60,
        "is_active": True
    }
]

# Политики для публикаций
post_policies = [
    {
        "name": "Политика автора публикации",
        "description": "Полный доступ к своим публикациям",
        "resource_type": ResourceType.POST,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value,
            PermissionType.DELETE.value,
            PermissionType.MANAGE.value
        ],
        "priority": 100,
        "is_active": True
    },
    {
        "name": "Политика модератора публикаций",
        "description": "Управление публикациями",
        "resource_type": ResourceType.POST,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value,
            PermissionType.MANAGE.value
        ],
        "priority": 90,
        "is_active": True
    },
    {
        "name": "Политика редактора публикаций",
        "description": "Редактирование публикаций",
        "resource_type": ResourceType.POST,
        "permissions": [
            PermissionType.READ.value,
            PermissionType.WRITE.value
        ],
        "priority": 80,
        "is_active": True
    },
    {
        "name": "Политика просмотра публикаций",
        "description": "Только просмотр публикаций",
        "resource_type": ResourceType.POST,
        "permissions": [
            PermissionType.READ.value
        ],
        "priority": 60,
        "is_active": True
    }
]

# Объединяем все политики в один словарь для удобства доступа
all_policies = {
    ResourceType.WORKSPACE.value: workspace_policies,
    ResourceType.TABLE.value: table_policies,
    ResourceType.LIST.value: list_policies,
    ResourceType.KANBAN.value: kanban_policies,
    ResourceType.POST.value: post_policies
}


class PolicyService(BaseService):
    """
    Сервис для управления политиками доступа.
    Предоставляет методы для создания и применения политик доступа.
    """

    def __init__(
        self,
        session: AsyncSession,
        access_service: Optional[AccessControlService] = None
    ):
        """
        Инициализирует сервис политик доступа.

        Args:
            session: Асинхронная сессия базы данных
            access_service: Сервис контроля доступа
        """
        super().__init__(session)
        self.access_service = access_service or AccessControlService(session)

    async def create_default_policies(self, workspace_id: int, owner_id: int):
        """
        Создает базовые политики доступа для нового рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства
            owner_id: ID владельца рабочего пространства
        """
        self.logger.info(
            f"Создание базовых политик доступа для рабочего пространства ID: {workspace_id}, "
            f"владелец ID: {owner_id}"
        )

        # Создаем политики для рабочего пространства
        for policy_data in workspace_policies:
            policy_create_schema = AccessPolicyCreateSchema(
                name=policy_data["name"],
                description=policy_data["description"],
                resource_type=policy_data["resource_type"].value,
                permissions=policy_data["permissions"],
                priority=policy_data["priority"],
                is_active=policy_data["is_active"],
                workspace_id=workspace_id
            )

            # Создаем политику
            policy_response = await self.access_service.create_policy(
                policy_data=policy_create_schema,
                current_user=CurrentUserSchema(id=owner_id, role=UserRole.ADMIN)
            )

            # Если это политика владельца (с наивысшим приоритетом), применяем её к владельцу
            if policy_data["priority"] >= 100:
                await self.access_service.apply_policy(
                    policy_id=policy_response.data.id,
                    resource_id=workspace_id,
                    subject_id=owner_id,
                    subject_type="user"
                )

        # Создаем политики для других типов ресурсов
        for resource_type, policies in all_policies.items():
            if resource_type != ResourceType.WORKSPACE.value:
                for policy_data in policies:
                    policy_create_schema = AccessPolicyCreateSchema(
                        name=policy_data["name"],
                        description=policy_data["description"],
                        resource_type=policy_data["resource_type"].value,
                        permissions=policy_data["permissions"],
                        priority=policy_data["priority"],
                        is_active=policy_data["is_active"],
                        workspace_id=workspace_id,
                        conditions=policy_data.get("conditions")
                    )

                    await self.access_service.create_policy(
                        policy_data=policy_create_schema,
                        current_user=CurrentUserSchema(id=owner_id, role=UserRole.ADMIN)
                    )

        self.logger.info(
            f"Базовые политики доступа успешно созданы для рабочего пространства ID: {workspace_id}"
        )

    async def apply_default_access_rules(
        self,
        resource_type: ResourceType,
        resource_id: int,
        workspace_id: int,
        owner_id: int
    ):
        """
        Применяет базовые правила доступа для нового ресурса.

        Args:
            resource_type: Тип ресурса
            resource_id: ID ресурса
            workspace_id: ID рабочего пространства
            owner_id: ID владельца ресурса
        """
        self.logger.info(
            f"Применение базовых правил доступа для ресурса типа {resource_type.value}, "
            f"ID: {resource_id}, рабочее пространство ID: {workspace_id}, владелец ID: {owner_id}"
        )

        # Получаем все политики для данного типа ресурса в рабочем пространстве
        policies = await self.access_service.get_policies(
            workspace_id=workspace_id,
            resource_type=resource_type.value,
            current_user=CurrentUserSchema(id=owner_id, role=UserRole.ADMIN)
        )

        # Применяем политику владельца к ресурсу
        for policy in policies:
            # Ищем политику с наивысшим приоритетом (обычно это политика владельца)
            if policy.priority >= 100:
                await self.access_service.apply_policy(
                    policy_id=policy.id,
                    resource_id=resource_id,
                    subject_id=owner_id,
                    subject_type="user"
                )
                self.logger.info(
                    f"Политика владельца (ID: {policy.id}) применена к ресурсу "
                    f"типа {resource_type.value}, ID: {resource_id}"
                )
                break
