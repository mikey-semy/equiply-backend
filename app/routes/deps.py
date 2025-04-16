# from functools import wraps
# from typing import Callable, Union
# from dishka.integrations.fastapi import FromDishka
# from fastapi import Depends
# from app.core.security.auth import get_current_user
# from app.core.exceptions.access import AccessDeniedException
# from app.models.v1.access import PermissionType, ResourceType
# from app.schemas import CurrentUserSchema
# from app.services.v1.access.service import AccessControlService


# def require_permission(
#     resource_type: Union[ResourceType, str],
#     permission: Union[PermissionType, str],
#     resource_id_param: str = "id"
# ):
#     """
#     Декоратор для проверки разрешений в эндпоинтах.

#     Args:
#         resource_type: Тип ресурса
#         permission: Требуемое разрешение
#         resource_id_param: Имя параметра, содержащего ID ресурса

#     Returns:
#         Callable: Декоратор для проверки разрешений
#     """
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         async def wrapper(
#             *args,
#             current_user: CurrentUserSchema = Depends(get_current_user),
#             access_service: FromDishka[AccessControlService],
#             **kwargs
#         ):
#             # Получаем ID ресурса из параметров
#             resource_id = kwargs.get(resource_id_param)
#             if resource_id is None:
#                 raise ValueError(f"Параметр '{resource_id_param}' не найден в аргументах функции")

#             # Проверяем разрешение
#             try:
#                 await access_service.authorize(
#                     user_id=current_user.id,
#                     resource_type=resource_type,
#                     resource_id=resource_id,
#                     permission=permission
#                 )
#             except AccessDeniedException as e:
#                 raise e

#             # Если проверка прошла успешно, вызываем оригинальную функцию
#             return await func(*args, current_user=current_user, **kwargs)

#         return wrapper

#     return decorator
