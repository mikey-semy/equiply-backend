# Алгоритм работы системы контроля доступа Equiply

Рассмотрим работу системы контроля доступа на конкретном примере с одним администратором и двумя пользователями.

**Участники примера**:
1. **Администратор Алексей (ID: 1)** - администратор системы
2. **Пользователь Мария (ID: 2)** - владелец рабочего пространства
3. **Пользователь Иван (ID: 3)** - обычный пользователь

### Шаг 1: Создание рабочего пространства

Мария создает новое рабочее пространство "Проект X" через API:

```json
POST /api/v1/workspaces/
{
  "name": "Проект X",
  "description": "Рабочее пространство для проекта X"
}
```


Что происходит в системе:

1. Создается запись в таблице `workspaces` с ID: 1, owner_id: 2 (Мария)
2. Мария автоматически добавляется в таблицу `workspace_members` с ролью OWNER
3. Система вызывает функцию `create_default_policies_for_workspace` из модуля `access.base`
4. Создаются базовые политики доступа для рабочего пространства:
    - "Политика владельца рабочего пространства" (ID: 1) с разрешениями READ, WRITE, DELETE, MANAGE, ADMIN
    - "Политика администратора рабочего пространства" (ID: 2) с разрешениями READ, WRITE, MANAGE
    - "Политика модератора рабочего пространства" (ID: 3) с разрешениями READ, WRITE, MANAGE
    - "Политика редактора рабочего пространства" (ID: 4) с разрешениями READ, WRITE
    - "Политика просмотра рабочего пространства" (ID: 5) с разрешениями READ

5. Также создаются политики для других типов ресурсов (таблиц, списков и т.д.)
6. Для Марии автоматически создается правило доступа в таблице `access_rules`, связывающее её (subject_id: 2) с политикой владельца (policy_id: 1) и рабочим пространством (resource_id: 1)


### Шаг 2: Добавление пользователя в рабочее пространство

Мария добавляет Ивана в рабочее пространство с ролью EDITOR:

```json
POST /api/v1/workspaces/1/members
{
  "user_id": 3,
  "role": "editor"
}
```


Что происходит в системе:

1. Система проверяет, имеет ли Мария разрешение MANAGE для рабочего пространства с ID 1:
    - Вызывается метод `authorize` в AccessControlService
    - Метод `check_permission` получает применимые правила через `get_applicable_rules`
    - Находится правило, связывающее Марию с политикой владельца
    - Проверяется, что политика предоставляет разрешение MANAGE
    - Проверка успешна, Мария имеет право добавлять пользователей
2. Иван добавляется в таблицу `workspace_members` с ролью EDITOR
3. Система находит политику "Политика редактора рабочего пространства" (ID: 4)
4. Создается правило доступа в таблице `access_rules`, связывающее Ивана (subject_id: 3) с политикой редактора (policy_id: 4) и рабочим пространством (resource_id: 1)


### Шаг 3: Создание таблицы в рабочем пространстве

Мария создает таблицу "Задачи" в рабочем пространстве:

```json
POST /api/v1/workspaces/1/tables
{
  "name": "Задачи",
  "description": "Таблица для отслеживания задач"
}
```


Что происходит в системе:

1. Система проверяет, имеет ли Мария разрешение WRITE для рабочего пространства с ID 1 (аналогично шагу 2)
2. Создается запись в таблице `table_definitions` с ID: 1, workspace_id: 1
3. Система вызывает функцию `apply_default_rules_for_resource`
4. Находится политика "Политика владельца таблицы" для ресурса типа TABLE
5. Создается правило доступа, связывающее Марию (subject_id: 2) с этой политикой и таблицей (resource_id: 1)

### Шаг 4: Проверка доступа к таблице

Иван пытается просмотреть таблицу "Задачи":
```
GET /api/v1/tables/1
```

Что происходит в системе:

1. Запрос проходит через декоратор `require_permission`, который требует разрешение READ для ресурса типа TABLE с ID 1
2. Вызывается метод `authorize` в `AccessControlService`
3. Метод `check_permission` проверяет:
   - Есть ли у Ивана прямые правила доступа к таблице? Нет.
   - Есть ли у Ивана роль в рабочем пространстве, к которому относится таблица?
     - Система определяет, что таблица принадлежит рабочему пространству с ID 1
     - Проверяется роль Ивана в этом рабочем пространстве (EDITOR)
     - Роль EDITOR имеет разрешение READ для ресурсов в рабочем пространстве
   - Проверка успешна, Иван имеет право просматривать таблицу

### Шаг 5: Попытка удаления таблицы

Иван пытается удалить таблицу "Задачи":

```
DELETE /api/v1/tables/1
```

Что происходит в системе:

1. Запрос проходит через декоратор `require_permission`, который требует разрешение DELETE для ресурса типа TABLE с ID 1
2. Вызывается метод `authorize` в `AccessControlService`
3. Метод `check_permission` проверяет:
   - Есть ли у Ивана прямые правила доступа к таблице? Нет.
   - Есть ли у Ивана роль в рабочем пространстве, к которому относится таблица?
     - Система определяет, что таблица принадлежит рабочему пространству с ID 1
     - Проверяется роль Ивана в этом рабочем пространстве (EDITOR)
     - Роль EDITOR не имеет разрешение DELETE для ресурсов в рабочем пространстве
   - Проверка не проходит, выбрасывается исключение AccessDeniedException
4. API возвращает ошибку 403 Forbidden

### Шаг 6: Создание политики с условиями

Администратор Алексей создает политику временного доступа:

```json
POST /api/v1/access/policies/
{
  "name": "Временный доступ к таблицам",
  "resource_type": "table",
  "permissions": ["read", "write"],
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

Что происходит в системе:

1. Система проверяет, имеет ли Алексей права администратора (current_user.role = ADMIN)
2. Создается запись в таблице `access_policies` с ID: 10, с указанными условиями и разрешениями

### Шаг 7: Применение политики к пользователю

Мария применяет политику временного доступа к Ивану для конкретной таблицы:

```json
POST /api/v1/access/rules/
{
  "policy_id": 10,
  "resource_id": 1,
  "resource_type": "table",
  "subject_id": 3,
  "subject_type": "user"
}
```

Что происходит в системе:

1. Система проверяет, имеет ли Мария разрешение MANAGE для рабочего пространства с ID 1
2. Создается запись в таблице access_rules, связывающая Ивана (subject_id: 3) с политикой временного доступа (policy_id: 10) и таблицей (resource_id: 1)

### Шаг 8: Проверка доступа с учетом условий

Иван пытается изменить данные в таблице "Задачи" в разное время суток:

```json
PUT /api/v1/tables/1/rows/5
{
  "name": "Обновленная задача",
  "status": "В процессе"
}
```

**Сценарий A: Запрос в рабочее время (10:30)**
Что происходит в системе:

1. Запрос проходит через декоратор require_permission, который требует разрешение WRITE для ресурса типа TABLE с ID 1
2. Вызывается метод `authorize` в `AccessControlService`
3. Метод `check_permission` получает применимые правила через `get_applicable_rules`
4. Находится правило, связывающее Ивана с политикой временного доступа
5. Метод `_evaluate_rule` проверяет условия политики:
   - Текущее время (10:30) находится в диапазоне 09:00-18:00
   - Условие выполнено, политика применяется
6. Проверка успешна, Иван имеет право изменять таблицу в рабочее время
7. Запрос обрабатывается, данные обновляются

**Сценарий B: Запрос вне рабочего времени (20:30)**
Что происходит в системе:

1. Запрос проходит через декоратор require_permission, который требует разрешение WRITE для ресурса типа TABLE с ID 1
2. Вызывается метод `authorize` в `AccessControlService`
3. Метод `check_permission` получает применимые правила через `get_applicable_rules`
4. Находится правило, связывающее Ивана с политикой временного доступа
5. Метод `_evaluate_rule` проверяет условия политики:
   - Текущее время (20:30) не находится в диапазоне 09:00-18:00
   - Условие не выполнено, политика не применяется
6. Система проверяет другие правила и роли:
   - Роль EDITOR в рабочем пространстве дает Ивану право WRITE без временных ограничений
   - Проверка успешна, Иван имеет право изменять таблицу
7. Запрос обрабатывается, данные обновляются

### Шаг 9: Изменение роли пользователя

Мария меняет роль Ивана с EDITOR на VIEWER:

```json
PUT /api/v1/workspaces/1/members/3
{
  "role": "viewer"
}
```

Что происходит в системе:

1. Система проверяет, имеет ли Мария разрешение MANAGE для рабочего пространства с ID 1
2. Обновляется запись в таблице `workspace_members`, роль Ивана меняется на VIEWER
3. Система находит политику "Политика просмотра рабочего пространства" (ID: 5)
4. Обновляется правило доступа в таблице `access_rules`, связывающее Ивана с политикой просмотра

### Шаг 10: Проверка доступа после изменения роли

Иван снова пытается изменить данные в таблице "Задачи" в рабочее время:

```json
PUT /api/v1/tables/1/rows/5
{
  "name": "Еще одно обновление",
  "status": "Завершено"
}
```
Что происходит в системе:

1. Запрос проходит через декоратор `require_permission`, который требует разрешение WRITE для ресурса типа TABLE с ID 1
2. Вызывается метод `authorize` в `AccessControlService`
3. Метод `check_permission` получает применимые правила через `get_applicable_rules`
4. Находится правило, связывающее Ивана с политикой временного доступа
5. Метод `_evaluate_rule` проверяет условия политики:
    - Текущее время находится в диапазоне 09:00-18:00
    - Условие выполнено, политика применяется
    - Политика предоставляет разрешение WRITE
6. Проверка успешна, Иван имеет право изменять таблицу в рабочее время, несмотря на роль VIEWER
7. Запрос обрабатывается, данные обновляются

### Шаг 11: Отключение политики временного доступа

Мария отключает политику временного доступа:

```json
PUT /api/v1/access/policies/10
{
  "is_active": false
}
```

Что происходит в системе:

1. Система проверяет, имеет ли Мария разрешение MANAGE для рабочего пространства с ID 1
2. Обновляется запись в таблице access_policies, поле is_active устанавливается в false

### Шаг 12: Проверка доступа после отключения политики
Иван снова пытается изменить данные в таблице "Задачи":

```json
PUT /api/v1/tables/1/rows/5
{
  "name": "Финальное обновление",
  "status": "Проверено"
}
```

Что происходит в системе:

1. Запрос проходит через декоратор `require_permission`, который требует разрешение WRITE для ресурса типа TABLE с ID 1
2. Вызывается метод `authorize` в `AccessControlService`
3. Метод `check_permission` получает применимые правила через `get_applicable_rules`
4. Правило с неактивной политикой игнорируется
5. Система проверяет роль Ивана в рабочем пространстве (VIEWER)
6. Роль VIEWER не имеет разрешение WRITE для ресурсов в рабочем пространстве
7. Проверка не проходит, выбрасывается исключение AccessDeniedException
8. API возвращает ошибку 403 Forbidden

### Шаг 13: Администратор получает доступ к ресурсам

Администратор Алексей пытается просмотреть таблицу "Задачи":
```
GET /api/v1/tables/1
```

Что происходит в системе:

1. Запрос проходит через декоратор `require_permission`, который требует разрешение READ для ресурса типа TABLE с ID 1
2. Вызывается метод `authorize` в `AccessControlService`
3. Метод `check_permission` проверяет:
    - Есть ли у Алексея прямые правила доступа к таблице? Нет.
    - Есть ли у Алексея роль в рабочем пространстве? Нет.
    - Является ли Алексей администратором системы? Да.
    - Администраторы имеют доступ ко всем ресурсам
4. Проверка успешна, Алексей имеет право просматривать таблицу
5. Запрос обрабатывается, данные возвращаются

### Заключение
Этот пример демонстрирует основные принципы работы системы контроля доступа Equiply:

1. Многоуровневая проверка доступа:

    - Проверка прямых правил доступа
    - Проверка ролей в рабочем пространстве
    - Проверка административных прав

2. Условные разрешения:

    - Политики могут содержать условия (время, дата и т.д.)
    - Условия проверяются в момент запроса

3. Приоритеты политик:

    - Политики с более высоким приоритетом применяются первыми
    - Это позволяет создавать исключения из общих правил

4. Иерархия ресурсов:

    - Доступ к ресурсу может определяться доступом к родительскому ресурсу
    - Например, роль в рабочем пространстве влияет на доступ к таблицам

5. Гибкость настройки:

    - Администраторы и владельцы ресурсов могут создавать собственные политики
    - Политики могут быть активированы и деактивированы по необходимости

Такой подход обеспечивает гибкую и надежную систему контроля доступа, которая может адаптироваться к различным требованиям безопасности и бизнес-процессам.