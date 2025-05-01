from functools import wraps
from typing import Callable, Union

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

    Returns:
        Callable: Декоратор для проверки разрешений

    Examples:
        ```python
        @router.delete("/{workspace_id}/members/{user_id}")
        @require_permission(
            resource_type=ResourceType.WORKSPACE,
            permission=PermissionType.MANAGE,
            resource_id_param="workspace_id"
        )
        async def remove_workspace_member(workspace_id: int, user_id: int):
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
        async def wrapper(
            *args,
            current_user: CurrentUserSchema = Depends(get_current_user),
            access_service: FromDishka[AccessControlService],
            **kwargs,
        ):
            # Получаем ID ресурса из параметров
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

            # Если проверка прошла успешно, вызываем оригинальную функцию
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator
