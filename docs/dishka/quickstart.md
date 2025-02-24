# Быстрый старт

1. **Установка Dishka.**

```shell
pip install dishka
```
2. **Определите ваши классы с подсказками типов.** Представьте, что у вас есть два класса: `Service` (бизнес-логика) и `DAO` (доступ к данным), вместе с внешним `API` клиентом:

```python
class DAO(Protocol):
    ...


class Service:
    def __init__(self, dao: DAO):
        ...


class DAOImpl(DAO):
    def __init__(self, connection: Connection):
        ...


class SomeClient:
    ...
```

3. **Создайте** экземпляр `Provider` и укажите как предоставлять зависимости.

Провайдеры используются только для настройки фабрик, предоставляющих ваши объекты.

Используйте scope=Scope.APP для зависимостей, 
создаваемых один раз на все время жизни приложения, 
и scope=Scope.REQUEST для тех, которые нужно пересоздавать для каждого запроса, события и т.д. 
Чтобы узнать больше о скоупах, смотрите [Scope management](https://dishka.readthedocs.io/en/stable/advanced/scopes.html#scopes)

```python
from dishka import Provider, Scope


service_provider = Provider(scope=Scope.REQUEST)
service_provider.provide(Service)
service_provider.provide(DAOImpl, provides=DAO)
service_provider.provide(SomeClient, scope=Scope.APP)  # override provider scope
```

Для предоставления соединения вам может понадобиться специальный код:

```python
from dishka import Provider, provide, Scope


class ConnectionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def new_connection(self) -> Iterable[Connection]:
        conn = sqlite3.connect(":memory:")
        yield conn
        conn.close()
```

4. **Создайте основной** экземпляр `Container`, передав провайдеры, и войдите в скоуп `APP`

```python
from dishka import make_container

container = make_container(service_provider, ConnectionProvider())
```

5. **Получайте доступ к зависимостям используя контейнер.** Контейнер хранит кэш зависимостей и используется для их получения. 
Вы можете использовать метод .get для доступа к зависимостям в скоупе APP:

```python
client = container.get(SomeClient)  # `SomeClient` has Scope.APP, so it is accessible here
client = container.get(SomeClient)  # same instance of `SomeClient`
```

6. **Входите и выходите** из скоупа `REQUEST` многократно используя контекстный менеджер:

```python
# subcontainer to access shorter-living objects
with container() as request_container:
    service = request_container.get(Service)
    service = request_container.get(Service)  # same service instance
# since we exited the context manager, the connection is now closed

# new subcontainer to have a new lifespan for request processing
with container() as request_container:
    service = request_container.get(Service)  # new service instance
```

7. **Закройте контейнер** когда закончите:

```python
container.close()
```

8. **Интегрируйтесь с вашим фреймворком.** Если вы используете поддерживаемый фреймворк, добавьте декораторы и middleware для него. 
Для более подробной информации смотрите [Using with frameworks](https://dishka.readthedocs.io/en/stable/integrations/index.html#integrations)]

```python
from dishka.integrations.fastapi import (
    FromDishka, inject, setup_dishka,
)

@router.get("/")
@inject
async def index(service: FromDishka[Service]) -> str:
    ...

...
setup_dishka(container, app)
```