# Инструкция по использованию системы контроля доступа в Equiply

## Часть 1: Использование API (для фронтенд-разработчиков)

### Основные концепции

Система контроля доступа Equiply построена на двух ключевых концепциях:

1. Политики доступа (Access Policies) - определяют набор разрешений для определенного типа ресурса
2. Правила доступа (Access Rules) - связывают политики с конкретными ресурсами и пользователями

### Эндпоинты API

#### Политики доступа
____
1. Создание политики доступа

```
POST /api/v1/access/policies/
```

Тело запроса:
```json
{
  "name": "Политика редакторов таблиц",
  "resource_type": "table",
  "permissions": ["read", "write"],
  "description": "Разрешает чтение и редактирование таблиц",
  "conditions": {
    "time_range": {
      "start": "09:00",
      "end": "18:00"
    }
  },
  "priority": 50,
  "workspace_id": 1
}
```

2. Получение списка политик

```
GET /api/v1/access/policies/?workspace_id=1&resource_type=table
```
Параметры запроса:

- `skip` - количество пропускаемых элементов (пагинация)
- `limit` - количество элементов на странице
- `sort_by` - поле для сортировки
- `sort_desc` - сортировка по убыванию (true/false)
- `workspace_id` - ID рабочего пространства
- `resource_type` - тип ресурса
- `name` - поиск по названию политики


3. Получение политики по ID

```
GET /api/v1/access/policies/{policy_id}
```

4. Обновление политики

```
PUT /api/v1/access/policies/{policy_id}
```

Тело запроса:
```json
{
  "name": "Обновленное название политики",
  "permissions": ["read", "write", "manage"],
  "is_active": true
}
```

5. Удаление политики
```
DELETE /api/v1/access/policies/{policy_id}
```

#### Правила доступа
____

1. Создание правила доступа

```
POST /api/v1/access/rules/
```

Тело запроса:
```json
{
  "policy_id": 1,
  "resource_id": 5,
  "resource_type": "table",
  "subject_id": 10,
  "subject_type": "user",
  "attributes": {
    "can_share": true
  }
}
```

2. Получение списка правил
```
GET /api/v1/access/rules/?policy_id=1&resource_type=table
```

Параметры запроса:

- `skip` - количество пропускаемых элементов (пагинация)
- `limit` - количество элементов на странице
- `sort_by` - поле для сортировки
- `sort_desc` - сортировка по убыванию
- `policy_id` - ID политики
- `resource_type` - тип ресурса
- `resource_id` - ID ресурса
- `subject_id` - ID субъекта
- `subject_type` - тип субъекта

3. Получение правила по ID
```
GET /api/v1/access/rules/{rule_id}
```

4. Обновление правила
```
PUT /api/v1/access/rules/{rule_id}
```

Тело запроса:
```json
{
  "attributes": {
    "can_share": false
  }
}
```

5. Удаление правила
```
DELETE /api/v1/access/rules/{rule_id}
```

#### Проверка разрешений
____

1. Проверка разрешения

```
POST /api/v1/access/check-permission/
```

Тело запроса:
```json
{
  "resource_type": "table",
  "resource_id": 5,
  "permission": "write",
  "context": {
    "time": "14:30"
  }
}
```


2. Получение всех разрешений пользователя для ресурса
```
GET /api/v1/access/user-permissions/table/5
```

#### Настройки доступа пользователя
____

1. Получение настроек доступа пользователя
```
GET /api/v1/access/settings/
```

2. Обновление настроек доступа пользователя
```
PUT /api/v1/access/settings/
```


Тело запроса:
```json
{
  "default_workspace_id": 1,
  "default_permission": "read"
}
```

#### Примеры использования
____

Пример 1: Настройка доступа к таблице

1. Создаем политику доступа для редакторов таблиц:
```
POST /api/v1/access/policies/
```

Тело запроса:
```json
{
  "name": "Редакторы таблиц",
  "resource_type": "table",
  "permissions": ["read", "write"],
  "description": "Разрешает чтение и редактирование таблиц",
  "priority": 50,
  "workspace_id": 1
}
```
2. Применяем политику к конкретной таблице и пользователю:
```
POST /api/v1/access/rules/
```

Тело запроса:
```json
{
  "policy_id": 1,
  "resource_id": 5,
  "resource_type": "table",
  "subject_id": 10,
  "subject_type": "user"
}
```

3. Проверяем, что пользователь имеет доступ:
```
POST /api/v1/access/check-permission/
```

Тело запроса:
```json
{
  "resource_type": "table",
  "resource_id": 5,
  "permission": "write"
}
```

## Часть 2: Программирование с использованием системы доступа (для бэкенд-разработчиков)

### Использование декоратора require_permission

Декоратор require_permission позволяет защитить эндпоинты API, требуя определенные разрешения для доступа к ресурсам.

#### Базовое использование
____
```python
from app.core.security.access import require_permission
from app.models.v1.access import ResourceType, PermissionType

@router.get("/{workspace_id}/tables/{table_id}")
@require_permission(
    resource_type=ResourceType.TABLE,
    permission=PermissionType.READ,
    resource_id_param="table_id"
)
async def get_table(workspace_id: int, table_id: int):
    # Код будет выполнен только если у пользователя есть разрешение READ для таблицы
    ...
```
#### Параметры декоратора
____
- `resource_type` - тип ресурса (из перечисления ResourceType или строка)
- `permission` - требуемое разрешение (из перечисления PermissionType или строка)
- `resource_id_param` - имя параметра в пути URL, содержащего ID ресурса (по умолчанию "id")

#### Примеры использования
1. Защита эндпоинта для управления рабочим пространством:
```python
@router.put("/{workspace_id}")
@require_permission(
    resource_type=ResourceType.WORKSPACE,
    permission=PermissionType.MANAGE,
    resource_id_param="workspace_id"
)
async def update_workspace(workspace_id: int, data: WorkspaceUpdateSchema):
    # Код выполнится только если у пользователя есть разрешение MANAGE для рабочего пространства
    ...
```

2. Защита эндпоинта для удаления записи в таблице:

```python
@router.delete("/tables/{table_id}/rows/{row_id}")
@require_permission(
    resource_type=ResourceType.TABLE,
    permission=PermissionType.WRITE,
    resource_id_param="table_id"
)
async def delete_table_row(table_id: int, row_id: int):
    # Код выполнится только если у пользователя есть разрешение WRITE для таблицы
    ...
```

3. Защита эндпоинта для просмотра канбан-доски:
```python
@router.get("/kanban/{kanban_id}")
@require_permission(
    resource_type=ResourceType.KANBAN,
    permission=PermissionType.READ,
    resource_id_param="kanban_id"
)
async def get_kanban_board(kanban_id: int):
    # Код выполнится только если у пользователя есть разрешение READ для канбан-доски
    ...
```


### Методы сервиса AccessControlService

### Проверка разрешений
- `check_permission(user_id, resource_type, resource_id, permission, context=None)` - проверяет наличие разрешения (возвращает bool)
- `authorize(user_id, resource_type, resource_id, permission, context=None)` - проверяет разрешение и выбрасывает исключение при отказе
- `get_user_permissions(user_id, resource_type, resource_id)` - возвращает список всех разрешений пользователя для ресурса

### Управление политиками
- `create_policy(policy_data, current_user)` - создает новую политику доступа
- `get_policies(pagination, workspace_id, resource_type, name, current_user)` - получает список политик с пагинацией
- `get_policy(policy_id, current_user)` - получает политику по ID
- `update_policy(policy_id, policy_data, current_user)` - обновляет политику
- `delete_policy(policy_id, current_user)` - удаляет политику

### Управление правилами
- `create_rule(rule_data, current_user)` - создает новое правило доступа
- `get_rules(pagination, policy_id, resource_type, resource_id, subject_id, subject_type, current_user)` - получает список правил с пагинацией
- `get_rule(rule_id, current_user)` - получает правило по ID
- `update_rule(rule_id, rule_data, current_user)` - обновляет правило
- `delete_rule(rule_id, current_user)` - удаляет правило