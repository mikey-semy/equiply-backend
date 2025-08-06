from functools import wraps
from typing import Callable, Union
import inspect
from dishka.integrations.fastapi import FromDishka
from fastapi import Depends
from app.core.exceptions.access import AccessDeniedException
from app.core.security.auth import get_current_user
from app.models.v1.access import PermissionType, ResourceType
from app.schemas import CurrentUserSchema
from app.services.v1.access.service import AccessControlService


def require_permission(
    resource_type: Union[ResourceType, str],
    permission: Union[PermissionType, str],
    resource_id_param: str = "id",
    from_body: bool = False,
):
    """
    Декоратор для проверки разрешений пользователя к ресурсам в эндпоинтах.

    Args:
        resource_type: Тип ресурса, к которому проверяется доступ.
            Возможные значения из ResourceType:
            - ResourceType.WORKSPACE - рабочее пространство
            - ResourceType.TABLE - таблица
            - ResourceType.LIST - список
            - ResourceType.KANBAN - канбан-доска
            - ResourceType.POST - публикация
            - ResourceType.USER - пользователь
            - ResourceType.CUSTOM - пользовательский тип ресурса

        permission: Требуемое разрешение для выполнения операции.
            Возможные значения из PermissionType:
            - PermissionType.READ - чтение ресурса
            - PermissionType.WRITE - изменение ресурса
            - PermissionType.DELETE - удаление ресурса
            - PermissionType.MANAGE - управление ресурсом (настройки, права)
            - PermissionType.ADMIN - полный административный доступ
            - PermissionType.CUSTOM - пользовательское разрешение

        resource_id_param: Имя параметра в пути URL, содержащего ID ресурса.
            По умолчанию "id". Примеры:
            - Для маршрута "/{workspace_id}/..." указать "workspace_id"
            - Для маршрута "/tables/{table_id}" указать "table_id"
            - Для маршрута "/users/{id}" можно использовать значение по умолчанию

        from_body: Флаг, указывающий, что ID ресурса передается в теле запроса.
            По умолчанию False. Если True, то ID ресурса будет искаться в теле запроса.

    Returns:
        Callable: Декоратор для проверки разрешений

    Examples:
        ```python
        @router.delete("/{workspace_id}/members/{user_id}")
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.MANAGE,
            resource_id_param="workspace_id",
        )
        async def remove_workspace_member(workspace_id: int, user_id: uuid.UUID):
            # Функция будет вызвана только если у пользователя есть
            # разрешение MANAGE для рабочего пространства с ID workspace_id
            ...

        @router.get("/tables/{table_id}")
        @require_permission(
            resource_type=ResourceType.TABLE,
            permission=PermissionType.READ,
            resource_id_param="table_id"
        )
        async def get_table(table_id: int):
            # Функция будет вызвана только если у пользователя есть
            # разрешение READ для таблицы с ID table_id
            ...
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем access_service и current_user из kwargs
            # Они должны быть переданы через DI в оригинальной функции
            access_service = None
            current_user = None

            # Ищем в kwargs
            for key, value in kwargs.items():
                if key == 'access_service' or isinstance(value, AccessControlService):
                    access_service = value
                elif key in ['current_user', '_current_user'] or isinstance(value, CurrentUserSchema):
                    current_user = value

            # Если не нашли в kwargs, пытаемся получить из DI контейнера
            if not access_service:
                # Здесь нужно получить access_service из вашего DI контейнера
                # Замените на ваш способ получения сервиса
                raise ValueError("AccessControlService не найден в параметрах")

            if not current_user:
                raise ValueError("CurrentUser не найден в параметрах")

            # Получаем ID ресурса из параметров
            resource_id = None
            if from_body:
                for arg in args:
                    if hasattr(arg, resource_id_param):
                        resource_id = getattr(arg, resource_id_param)
                        break
            else:
                resource_id = kwargs.get(resource_id_param)

            if resource_id is None:
                raise ValueError(
                    f"Параметр '{resource_id_param}' не найден в аргументах функции"
                )

            # Проверяем разрешение
            try:
                await access_service.authorize(
                    user_id=current_user.id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    permission=permission,
                )
            except AccessDeniedException as e:
                raise e

            # Вызываем оригинальную функцию
            return await func(*args, **kwargs)

        return wrapper

    return decorator
