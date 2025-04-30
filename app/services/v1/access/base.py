from app.models.v1.access import ResourceType, PermissionType

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

# # Функция для создания базовых политик при инициализации рабочего пространства
# async def create_default_policies_for_workspace(
#     access_service,
#     workspace_id: int,
#     owner_id: int
# ):
#     """
#     Создает базовые политики доступа для нового рабочего пространства.

#     Args:
#         access_service: Сервис контроля доступа
#         workspace_id: ID рабочего пространства
#         owner_id: ID владельца рабочего пространства
#     """
#     # Создаем политики для рабочего пространства
#     for policy_data in workspace_policies:
#         policy_data_copy = policy_data.copy()
#         policy_data_copy["workspace_id"] = workspace_id
#         policy_data_copy["owner_id"] = owner_id
#         await access_service.data_manager.create_policy(policy_data_copy)

#     # Создаем политики для других типов ресурсов
#     for resource_type, policies in all_policies.items():
#         if resource_type != ResourceType.WORKSPACE.value:
#             for policy_data in policies:
#                 policy_data_copy = policy_data.copy()
#                 policy_data_copy["workspace_id"] = workspace_id
#                 policy_data_copy["owner_id"] = owner_id
#                 await access_service.data_manager.create_policy(policy_data_copy)

# # Функция для применения базовых правил доступа при создании ресурса
# async def apply_default_rules_for_resource(
#     access_service,
#     resource_type: ResourceType,
#     resource_id: int,
#     workspace_id: int,
#     owner_id: int
# ):
#     """
#     Применяет базовые правила доступа для нового ресурса.

#     Args:
#         access_service: Сервис контроля доступа
#         resource_type: Тип ресурса
#         resource_id: ID ресурса
#         workspace_id: ID рабочего пространства
#         owner_id: ID владельца ресурса
#     """
#     # Получаем политики для данного типа ресурса в рабочем пространстве
#     policies = await access_service.data_manager.get_policies(
#         workspace_id=workspace_id,
#         resource_type=resource_type.value
#     )

#     # Применяем политику владельца к ресурсу
#     for policy in policies:
#         # Ищем политику с наивысшим приоритетом (обычно это политика владельца)
#         if policy.priority >= 100:
#             await access_service.apply_policy(
#                 policy_id=policy.id,
#                 resource_id=resource_id,
#                 subject_id=owner_id,
#                 subject_type="user"
#             )
#             break