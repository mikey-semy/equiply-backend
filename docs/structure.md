Структура проекта Equiply Backend

1. Модели (app/models/v1/...)
   - Базовые модели: app/models/v1/base.py
   - Модели пользователей: app/models/v1/users.py
   - Модели доступа: app/models/v1/access.py
   - Модели рабочих пространств: app/models/v1/workspaces.py
   - ...

2. Схемы (app/schemas/v1/...)
   - Базовые схемы: app/schemas/v1/base.py
   - Схемы пользователей:
     - Базовые: app/schemas/v1/users/base.py
     - Запросы: app/schemas/v1/users/requests.py
     - Ответы: app/schemas/v1/users/responses.py
     - Исключения: app/schemas/v1/users/exceptions.py
   - ...

3. Сервисы (app/services/v1/...)
   - Базовый сервис: app/services/v1/base.py
   - Сервисы пользователей:
     - Сервис: app/services/v1/users/service.py
     - Менеджер данных: app/services/v1/users/data_manager.py
   - ...

4. Роутеры (app/routes/v1/...)
   - Базовый роутер: app/routes/base.py
   - Роутер пользователей: app/routes/v1/users.py
   - ...

5. Исключения (app/core/exceptions/...)
   - Базовые исключения: app/core/exceptions/base.py
   - Исключения доступа: app/core/exceptions/access.py
   - Исключения пользователей: app/core/exceptions/users.py
   - ...

6. Зависимости (app/core/dependencies/...)
   - Контейнер: app/core/dependencies/container.py
   - Провайдеры: app/core/dependencies/providers/...
     - Провайдер пользователей: app/core/dependencies/providers/users.py
     - Провайдер доступа: app/core/dependencies/providers/access.py
     - ...

7. Жизненный цикл (app/core/lifespan/...)
   - Базовый модуль: app/core/lifespan/base.py
   - Инициализация доступа: app/core/lifespan/access.py
   - ...

8. Безопасность (app/core/security/...)
   - Аутентификация: app/core/security/auth.py
   - Контроль доступа: app/core/security/access.py
   - ...

9. Настройки (app/core/settings/...)
   - Базовые настройки: app/core/settings/base.py
   - ...

10. Интеграции (app/core/integrations/...)
    - HTTP: app/core/integrations/http/...
    - Кэш: app/core/integrations/cache/...
    - ...

Примеры структуры компонентов:

1. Провайдер:

```python
from dishka import Provider, Scope, provide
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.users.service import UserService

class UserProvider(Provider):
@provide(scope=Scope.REQUEST)
def user_service(self, db_session: AsyncSession, redis: Redis) -> UserService:
    return UserService(db_session, redis)
```

2. Контейнер:

```python
from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider
from .providers.users import UserProvider

#...
container = make_async_container(
    UserProvider(),
    # ...
    )
```

3. Роутер:



```python
        @self.router.post(
            path="/rules/",
            response_model=AccessRuleCreateResponseSchema,
            status_code=201,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            },
        )
        @inject
        async def create_rule(
            rule_data: AccessRuleCreateRequestSchema,
            access_service: FromDishka[AccessControlService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleCreateResponseSchema:
            """
            ## ➕ Создание правила доступа

            Создает новое правило доступа на основе существующей политики.

            ### Тело запроса:
            * **policy_id**: ID политики доступа
            * **resource_id**: ID ресурса
            * **resource_type**: Тип ресурса
            * **subject_id**: ID субъекта (пользователя или группы)
            * **subject_type**: Тип субъекта ('user' или 'group')
            * **attributes**: Дополнительные атрибуты правила (опционально)

            ### Returns:
            * Созданное правило доступа
            """
            return await access_service.create_rule(
                rule_data=rule_data, current_user=current_user
            )
```

4. Схема исключения:




from pydantic import Field from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

class UserNotFoundErrorSchema(ErrorSchema): detail: str = "Пользователь не найден" error_type: str = "user_not_found" status_code: int = 404

class UserNotFoundResponseSchema(ErrorResponseSchema): error: UserNotFoundErrorSchema


5. Исключение:




from app.core.exceptions.base import BaseAPIException

class UserNotFoundException(BaseAPIException): status_code = 404 error_code = "user_not_found" detail = "Пользователь не найден"


6. Сервис:




from sqlalchemy.ext.asyncio import AsyncSession from redis import Redis from app.services.v1.base import BaseService from app.services.v1.users.data_manager import UserDataManager

class UserService(BaseService): def init(self, session: AsyncSession, redis: Redis): super().init(session) self.data_manager = UserDataManager(session) self.redis = redis

async def get_user(self, user_id: int):
    # Логика получения пользователя
    pass





7. Менеджер данных:




from sqlalchemy.ext.asyncio import AsyncSession from app.services.v1.base import BaseEntityManager from app.models.v1.users import UserModel from app.schemas.v1.users.base import UserSchema

class UserDataManager(BaseEntityManager[UserSchema]): def init(self, session: AsyncSession): super().init(session, UserSchema, UserModel)

async def get_user_by_id(self, user_id: int):
    # Логика получения пользователя из БД
    pass




"""




Этот файл можно использовать как шпаргалку при разработке новых компонентов, чтобы не забывать структуру проекта и правильно организовывать код.

Для реализации групп пользователей нужно будет создать все необходимые компоненты согласно этой структуре:

Модели: app/models/v1/groups.py
Схемы:
app/schemas/v1/groups/base.py
app/schemas/v1/groups/requests.py
app/schemas/v1/groups/responses.py
app/schemas/v1/groups/exceptions.py
Сервисы:
app/services/v1/groups/service.py
app/services/v1/groups/data_manager.py
Роутер: app/routes/v1/groups.py
Провайдер: app/core/dependencies/providers/groups.py
И не забыть зарегистрировать провайдер в контейнере и добавить роутер в приложение.