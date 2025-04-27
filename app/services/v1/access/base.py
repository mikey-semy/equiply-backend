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

# Аналогично для других типов ресурсов
table_policies = [...]
list_policies = [...]
kanban_policies = [...]
post_policies = [...]
