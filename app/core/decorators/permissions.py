"""
Модуль содержит декораторы для работы с разрешениями (permissions).

Основная проблема, которую решает этот модуль - несоответствие форматов хранения
разрешений в базе данных (словарь) и в API (список). Декоратор transform_permissions
автоматически преобразует данные между этими форматами.

Архитектурное решение:
1. В моделях БД разрешения хранятся как Dict[str, bool] для эффективности
2. В API разрешения представлены как List[str] для читаемости
3. Декоратор transform_permissions автоматизирует преобразование между форматами

Пример использования:
    @transform_permissions(input_param="policy_data", output_transform=True)
    async def create_policy(self, policy_data: dict) -> PolicySchema:
        # Здесь policy_data["permissions"] уже преобразован из списка в словарь
        policy = PolicyModel(**policy_data)
        # ...
        # В возвращаемом объекте permissions будет преобразован обратно в список
        return policy
"""
import logging
import functools
from typing import Callable, TypeVar, cast

from app.models.v1.base import BaseModel

T = TypeVar('T')

logger = logging.getLogger(__name__)

def transform_permissions(
    input_param: str = None,
    output_transform: bool = True,
    input_is_dict: bool = False
):
    """
    Декоратор для автоматического преобразования поля permissions между форматами списка и словаря.

    Этот декоратор решает проблему несоответствия форматов хранения разрешений:
    - В моделях БД разрешения хранятся как словарь (Dict[str, bool]) для эффективности
    - В API разрешения представлены как список (List[str]) для читаемости

    Преимущества использования словаря в БД:
    - Эффективная проверка наличия разрешения за O(1) вместо O(n) для списка
    - Возможность хранить явно запрещенные действия: {"read": true, "write": false}
    - Расширяемость для добавления метаданных к разрешениям
    - Лучшая совместимость с JSON-полями в БД при частичных обновлениях

    Преимущества использования списка в API:
    - Простота и читаемость: ["read", "write", "manage"]
    - Компактность в JSON-ответах
    - Удобство для фронтенд-разработчиков при работе с UI-компонентами
    - Соответствие REST-принципам для перечисления возможностей
    Args:
        input_param: Имя параметра, содержащего входные данные с полем permissions
        output_transform: Нужно ли преобразовывать permissions в выходных данных
        input_is_dict: Если True, преобразует permissions из словаря в список, иначе наоборот

    Returns:
        Декорированная функция
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.debug("Вызов декорированной функции: %s", func.__name__)
            # Преобразование входных данных
            if input_param and input_param in kwargs:
                data = kwargs[input_param]

                logger.debug(
                    "Входные данные для %s: %s",
                    func.__name__,
                    {k: v for k, v in data.items() if k != "permissions"} if isinstance(data, dict) else data
                )

                if isinstance(data, dict) and "permissions" in data:
                    logger.debug(
                        "Тип permissions до преобразования: %s, значение: %s",
                        type(data["permissions"]),
                        data["permissions"]
                    )

                    if input_is_dict:
                        # Из словаря в список
                        if isinstance(data["permissions"], dict):
                            data["permissions"] = BaseModel.dict_to_list_field(data["permissions"])
                            logger.debug("Преобразовано из словаря в список")
                    else:
                        # Из списка в словарь
                        if isinstance(data["permissions"], list):
                            data["permissions"] = BaseModel.list_to_dict_field(data["permissions"])
                            logger.debug("Преобразовано из списка в словарь")

                    logger.debug(
                        "Тип permissions после преобразования: %s, значение: %s",
                        type(data["permissions"]),
                        data["permissions"]
                    )
            # Вызов оригинальной функции
            result = await func(*args, **kwargs)

            # Логируем результат для отладки
            if result:
                if hasattr(result, 'permissions'):
                    logger.debug(
                        "Тип permissions в результате до преобразования: %s, значение: %s",
                        type(result.permissions),
                        result.permissions
                    )

            # Преобразование выходных данных
            if output_transform and result:
                if hasattr(result, 'permissions'):
                    # Для одиночного объекта
                    if input_is_dict:
                        # Из словаря в список
                        if isinstance(result.permissions, dict):
                            result.permissions = BaseModel.dict_to_list_field(result.permissions)
                            logger.debug("Результат: преобразовано из словаря в список")
                    else:
                        # Из списка в словарь
                        if isinstance(result.permissions, list):
                            result.permissions = BaseModel.list_to_dict_field(result.permissions)
                            logger.debug("Результат: преобразовано из списка в словарь")

                    logger.debug(
                        "Тип permissions в результате после преобразования: %s, значение: %s",
                        type(result.permissions),
                        result.permissions
                    )
                elif isinstance(result, tuple) and len(result) > 0 and isinstance(result[0], list):
                    # Для списка объектов (например, в пагинации)
                    for item in result[0]:
                        if hasattr(item, 'permissions'):
                            if input_is_dict:
                                # Из словаря в список
                                if isinstance(item.permissions, dict):
                                    item.permissions = BaseModel.dict_to_list_field(item.permissions)
                            else:
                                # Из списка в словарь
                                if isinstance(item.permissions, list):
                                    item.permissions = BaseModel.list_to_dict_field(item.permissions)

            return result

        return cast(Callable[..., T], wrapper)

    return decorator
