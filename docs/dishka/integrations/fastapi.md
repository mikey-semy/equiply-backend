.. _fastapi:

FastAPI
===========================================

Хотя это не обязательно, вы можете использовать интеграцию dishka-fastapi. Она предоставляет:

* автоматическое управление областями видимости `REQUEST` и `SESSION` с помощью middleware
* передачу объекта `Request` в качестве контекстных данных провайдерам как для **Websockets**, так и для **HTTP** запросов
* автоматическое внедрение зависимостей в функцию-обработчик


Как использовать
****************

1. Импорт

```python
from dishka.integrations.fastapi import (
        DishkaRoute,
        FromDishka,
        FastapiProvider,
        inject,
        setup_dishka,
    )
    from dishka import make_async_container, Provider, provide, Scope
```

    

2. Создайте провайдер. Вы можете использовать `fastapi.Request` как параметр фабрики для доступа в области REQUEST-scope, и `fastapi.WebSocket` в области `SESSION` scope.

```python
class YourProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def create_x(self, request: Request) -> X:
         ...
```

3. *(необязательно)* Установите класс маршрута для каждого из ваших роутеров fastapi, чтобы включить автоматическое внедрение (работает только для HTTP, не для websockets).

```python
router = APIRouter(route_class=DishkaRoute)
```

3. Отметьте те параметры ваших обработчиков, которые должны быть внедрены с помощью `FromDishka[]`

```python
@router.get('/')
async def endpoint(
    request: str, gateway: FromDishka[Gateway],
) -> Response:
    ...
```

3a. (необязательно) декорируйте их с помощью `@inject`, если вы не используете DishkaRoute или используете websockets.

```python
@router.get('/')
@inject
async def endpoint(
    gateway: FromDishka[Gateway],
) -> ResponseModel:
    ...
```


4. *(необязательно)* Используйте `FastapiProvider()` при создании контейнера, если вы собираетесь использовать `fastapi.Request` или `fastapi.WebSocket` в провайдерах.

```python
container = make_async_container(YourProvider(), FastapiProvider())
```


5. *(необязательно)* Настройте lifespan для закрытия контейнера при завершении работы приложения

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()

app = FastAPI(lifespan=lifespan)
```

5. Настройте интеграцию dishka.

```python
setup_dishka(container=container, app=app)
```


Websockets
**********************

Для большинства случаев мы работаем с отдельными событиями, такими как HTTP-запросы. В этом случае мы используем только 2 области видимости: `APP` и `REQUEST`. WebSocket работают иначе: для одного приложения у вас есть несколько соединений (по одному на клиента), и каждое соединение передает множество сообщений. Для поддержки этого мы используем дополнительную область видимости: `SESSION`:

> APP → SESSION → REQUEST

В fastapi ваша функция представления вызывается один раз для соединения, а затем вы получаете сообщения в цикле. Поэтому декоратор `inject` может использоваться только для получения объектов с областью видимости SESSION. Для достижения области REQUEST вы можете войти в неё вручную:

```python
@inject
async def get_with_request(
    websocket: WebSocket,
    a: FromDishka[A],  # объект с Scope.SESSION
    container: FromDishka[AsyncContainer],  # контейнер для Scope.SESSION
) -> None:
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # входим во вложенную область видимости, которая является Scope.REQUEST
        async with container() as request_container:
            b = await request_container.get(B)  # объект с Scope.REQUEST
```
