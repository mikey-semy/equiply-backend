### 🎯 Основные концепции
1. Декораторы (Decorators)

```python
def require_permission(...):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # логика
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```
Что происходит:

- require_permission - это фабрика декораторов (decorator factory)
- Она возвращает настоящий декоратор decorator
- decorator оборачивает оригинальную функцию в wrapper
Изучить: `Декораторы Python`, `functools.wraps`, `замыкания (closures)`

2. Интроспекция функций (Function Introspection)
```python
sig = inspect.signature(func)  # Получаем сигнатуру функции
new_params = []
for param_name, param in sig.parameters.items():
    new_params.append(param)
```

Что происходит:

- inspect.signature() извлекает информацию о параметрах функции
- Мы можем программно анализировать и модифицировать сигнатуру
- Это позволяет динамически добавлять параметры
Изучить: `Модуль inspect`, `рефлексия в Python`, `метапrogramming`

3. Динамическое изменение сигнатуры

```python
new_params.append(
    inspect.Parameter(
        'current_user',
        inspect.Parameter.KEYWORD_ONLY,  # Только именованный параметр
        default=Depends(get_current_user),
        annotation=CurrentUserSchema
    )
)
new_sig = sig.replace(parameters=new_params)
wrapper.__signature__ = new_sig  # Применяем новую сигнатуру

```

Что происходит:

- Создаем новые параметры программно
- KEYWORD_ONLY означает, что параметр можно передать только по имени
- Заменяем сигнатуру wrapper'а, чтобы FastAPI "видел" новые параметры

4. Dependency Injection в FastAPI

```python
default=Depends(get_current_user)  # FastAPI DI
default=FromDishka[AccessControlService]  # Dishka DI
```

Что происходит:

- FastAPI автоматически вызывает функции-зависимости
- Depends() - встроенная система DI FastAPI
- FromDishka[] - интеграция с внешним DI контейнером Dishka

### 🔄 Как это работает пошагово

#### Этап 1: Применение декоратора
```python
@require_permission(ResourceType.WORKSPACE, PermissionType.READ, "workspace_id")
async def get_workspace(workspace_id: int, workspace_service: FromDishka[WorkspaceService]):
    pass
```

1. Вызывается require_permission() с параметрами
2. Возвращается decorator
3. decorator применяется к get_workspace

#### Этап 2: Модификация сигнатуры
Оригинальная функция:

```python
async def get_workspace(workspace_id: int, workspace_service: FromDishka[WorkspaceService])
```

Становится:

```python
async def wrapper(
    workspace_id: int, 
    workspace_service: FromDishka[WorkspaceService],
    current_user: CurrentUserSchema = Depends(get_current_user),  # Добавлено
    access_service: AccessControlService = FromDishka[AccessControlService]  # Добавлено
)
```

#### Этап 3: Выполнение запроса
1. FastAPI видит новую сигнатуру
2. Автоматически разрешает все зависимости
3. Вызывает wrapper с полным набором параметров
4. wrapper выполняет проверку доступа
5. Если проверка прошла - вызывает оригинальную функцию

### 🧠 Что нужно изучить для полного понимания

#### Базовый уровень:
1. Python основы:

- Декораторы и functools.wraps
- *args и **kwargs
- Замыкания (closures)
- Типизация (typing модуль)

2. Асинхронное программирование:

- async/await
- Корутины

#### Продвинутый уровень:
3. Метапрограммирование:

- Модуль inspect
- Динамическое создание функций
- Манипуляция сигнатурами функций

4. Паттерны проектирования:

- Dependency Injection
- Decorator Pattern
- Factory Pattern

#### Веб-разработка:
5. FastAPI:

- Система зависимостей (Depends)
- Middleware
- Обработка исключений

6. Архитектурные паттерны:

- RBAC (Role-Based Access Control)
- ABAC (Attribute-Based Access Control)
- Middleware pattern

### 🔍 Практический пример работы
```python 
# 1. Декоратор применяется
@require_permission(ResourceType.WORKSPACE, PermissionType.READ, "workspace_id")
async def get_workspace(workspace_id: int):
    return {"workspace_id": workspace_id}

# 2. FastAPI "видит" такую сигнатуру:
async def wrapper(
    workspace_id: int,
    current_user: CurrentUserSchema = Depends(get_current_user),
    access_service: AccessControlService = FromDishka[AccessControlService]
):
    # 3. Проверка доступа
    await access_service.authorize(
        user_id=current_user.id,
        resource_type=ResourceType.WORKSPACE,
        resource_id=workspace_id,  # Из URL параметра
        permission=PermissionType.READ,
    )
    
    # 4. Если проверка прошла - вызов оригинальной функции
    return await get_workspace(workspace_id)  # Только с оригинальными параметрами
```