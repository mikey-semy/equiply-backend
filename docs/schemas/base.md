Система базовых схем предоставляет унифицированную структуру для работы с входящими запросами и исходящими ответами в API, обеспечивает консистентность API, упрощает валидацию данных и делает код более читаемым и поддерживаемым.

**Рекомендации**

1. Именование схем
- `Request`: {Entity}{Action}RequestSchema (`UserCreateRequestSchema`, `ProductUpdateRequestSchema`)
- `Base`: {Entity}Schema (`UserSchema`, `ProductSchema`) 
- `Data`: {Entity}DataSchema (`UserDataSchema`, `ProductDataSchema`)
- `Response`: {Entity}{Action}ResponseSchema (`UserCreateResponseSchema`)

2. Структура файлов
```
app/schemas/v1/users/
├── __init__.py
├── base.py          # Базовые схемы сущностей
├── requests.py       # Схемы для входящих данных
└── responses.py      # Схемы для ответов
```
3. Валидация
```python
class UserCreateSchema(BaseRequestSchema):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username должен содержать только буквы и цифры')
        return v
```

3. Использование в сервисах (херовый пример)
```python
async def create_user(
    self, 
    user_data: UserCreateRequestSchema
) -> UserCreateResponseSchema:
    # Создание пользователя
    user = await self.data_manager.create_user(user_data.model_dump())
    
    # Преобразование в схему ответа
    user_schema = UserSchema.model_validate(user)
    
    return UserCreateResponseSchema(
        message="Пользователь успешно создан",
        data=user_schema
    )
```
**Описание:**

**Иерархия базовых схем:**
```
CommonBaseSchema
├── BaseSchema (+ id, created_at, updated_at)
├── BaseRequestSchema (для входных данных)
├── BaseCommonResponseSchema (базовый ответ без success/message)
└── BaseResponseSchema (+ success, message)
    ├── ErrorResponseSchema
    ├── ItemResponseSchema[T]
    ├── ListResponseSchema[T]
    └── MetaResponseSchema
```
**Описание атрибутов**
**CommonBaseSchema**:
- `model_config` - конфигурация Pydantic (from_attributes=True)
- `to_dict()` - преобразовать объект в словарь

**BaseSchema**:
наследует CommonBaseSchema
- `id` - идентификатор записи (Optional[int])
- `created_at` - дата создания (Optional[datetime])
- `updated_at` - дата обновления (Optional[datetime])

**BaseRequestSchema**:
наследует `CommonBaseSchema`
пустой класс для входных данных (без id и дат)

**BaseCommonResponseSchema**:
наследует `CommonBaseSchema`
пустой класс для ответов без success/message

**BaseResponseSchema**:
наследует `CommonBaseSchema`
- `success` - успешность запроса (bool, по умолчанию True)
- `message` - сообщение ответа (Optional[str])

**ErrorSchema**:
наследует `CommonBaseSchema`
- `detail` - описание ошибки (str)
- `error_type` - тип ошибки (str)
- `status_code` - HTTP код (int)
- `timestamp` - время ошибки (str)
- `request_id` - ID запроса (str)
- `extra` - дополнительные данные (Optional[Dict])

**ErrorResponseSchema**:
наследует `BaseResponseSchema`
- `success` - всегда False
- `message` - всегда None
- `data` - всегда None
- `error` - детали ошибки (`ErrorSchema`)

**ItemResponseSchema[T]**:
наследует BaseResponseSchema
- `item` - один элемент типа T

**ListResponseSchema[T]**:
наследует BaseResponseSchema
- `items` - список элементов типа T

**MetaResponseSchema**:
наследует BaseResponseSchema
- `meta` - метаданные ответа (dict)```


**Схемы для Request (входящие данные)**
**BaseRequestSchema**

Используется для всех входящих данных от клиента. 
Не содержит системные поля (`id`, `created_at`, `updated_at`).

Когда использовать:

- Создание новых записей
- Обновление существующих записей
- Фильтры и параметры поиска

Пример использования:
```python
from app.schemas.v1.base import BaseRequestSchema
from pydantic import Field, EmailStr

class UserCreateSchema(BaseRequestSchema):
    """Схема для создания пользователя."""
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: str | None = Field(None, pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$")

class UserUpdateSchema(BaseRequestSchema):
    """Схема для обновления пользователя."""
    username: str | None = Field(None, min_length=2, max_length=50)
    phone: str | None = Field(None, pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$")
    
    class Config:
        extra = "forbid"  # Запретить дополнительные поля

class UserFilterSchema(BaseRequestSchema):
    """Схема для фильтрации пользователей."""
    role: UserRole | None = None
    is_active: bool | None = None
    search: str | None = Field(None, max_length=100)
```

**Схемы для Response (исходящие данные)**
**BaseSchema**

Используется для представления данных сущностей с системными полями (`id`, `created_at`, `updated_at`).

```python
from app.schemas.v1.base import BaseSchema
from pydantic import EmailStr

class UserSchema(BaseSchema):
    """Основная схема пользователя."""
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool = True
    is_verified: bool = False
    is_online: bool = False
```


**BaseResponseSchema**
Базовая схема для всех ответов API с полями success и message.

```python
from app.schemas.v1.base import BaseResponseSchema

class UserCreateResponseSchema(BaseResponseSchema):
    """Ответ при создании пользователя."""
    message: str = "Пользователь успешно создан"
    data: UserDetailSchema

class UserUpdateResponseSchema(BaseResponseSchema):
    """Ответ при обновлении пользователя."""
    message: str = "Пользователь успешно обновлен"
    data: UserDetailSchema

class UserDeleteResponseSchema(BaseResponseSchema):
    """Ответ при удалении пользователя."""
    message: str = "Пользователь успешно удален"
    # data не указываем, если не нужно возвращать данные
```

**Специализированные Response схемы**

**ItemResponseSchema[T]**
Для ответов с одним элементом:

```python
from app.schemas.v1.base import ItemResponseSchema

class UserItemResponseSchema(ItemResponseSchema[UserSchema]):
    """Ответ с одним пользователем."""
    message: str = "Пользователь успешно получен"
```

**ListResponseSchema[T]**
Для ответов со списком элементов:

```python
from app.schemas.v1.base import ListResponseSchema

class UserListResponseSchema(ListResponseSchema[UserSchema]):
    """Ответ со списком пользователей."""
    message: str = "Список пользователей получен"
```

**MetaResponseSchema**
Для ответов с метаданными:

```python
from app.schemas.v1.base import MetaResponseSchema

class UserStatsResponseSchema(MetaResponseSchema):
    """Ответ со статистикой пользователей."""
    message: str = "Статистика получена"
    meta: dict  # Содержит статистические данные
```