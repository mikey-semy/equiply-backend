import logging
from typing import Any, Callable, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import and_, asc, delete, desc, func, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.expression import Executable

from app.models.v1.base import BaseModel
from app.schemas.v1.base import BaseSchema
from app.schemas.v1.pagination import PaginationParams

M = TypeVar("M", bound=BaseModel)
T = TypeVar("T", bound=BaseSchema)


class SessionMixin:
    """
    Миксин для предоставления экземпляра сессии базы данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует SessionMixin.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
        """
        self.session = session


class BaseService(SessionMixin):
    """
    Базовый класс для сервисов приложения.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.logger = logging.getLogger(self.__class__.__name__)


class BaseDataManager(SessionMixin, Generic[T]):
    """
    Базовый класс для менеджеров данных с поддержкой обобщенных типов.

    Attributes:
        session (AsyncSession): Асинхронная сессия базы данных.
        schema (Type[T]): Тип схемы данных.
        model (Type[M]): Тип модели.
    """

    def __init__(self, session: AsyncSession, schema: Type[T], model: Type[M]):
        """
        Инициализирует BaseDataManager.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            schema (Type[T]): Тип схемы данных.
            model (Type[M]): Тип модели.
        """
        super().__init__(session)
        self.schema = schema
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    async def add_one(self, model: M) -> M:
        """
        Добавляет одну запись в базу данных.

        Args:
            model (M): Модель SQLAlchemy для добавления.

        Returns:
            M: Добавленная запись в виде модели SQLAlchemy.

        Raises:
            SQLAlchemyError: Если произошла ошибка при добавлении.

        Example:
            # Создание новой модели и добавление её в БД
            new_user = User(username="john_doe", email="john@example.com")
            user_model = await data_manager.add_one(new_user)
        """
        try:
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return model
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при добавлении: %s", e)
            raise

    async def get_one(self, select_statement: Executable) -> M | None:
        """
        Получает одну запись из базы данных.

        Args:
            select_statement (Executable): SQL-запрос для выборки.

        Returns:
            M | None: Полученная SQLAlchemy модель или None, если запись не найдена.

        Raises:
            SQLAlchemyError: Если произошла ошибка при получении записи.

        Usage:
            # Получение пользователя по ID
            statement = select(User).where(User.id == user_id)
            user = await data_manager.get_one(statement)

            # Получение первого активного пользователя
            statement = select(User).where(User.is_active == True).limit(1)
            active_user = await data_manager.get_one(statement)
        """
        try:
            self.logger.info("Получение записи из базы данных")
            self.logger.debug("SQL-запрос: %s", select_statement)
            result = await self.session.execute(select_statement)
            return result.scalar()
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при получении записи: %s", e)
            raise

    async def get_all(self, select_statement: Executable) -> List[M]:
        """
        Получает все записи из базы данных.

        Args:
            select_statement (Executable): SQL-запрос для выборки.

        Returns:
            List[M]: Список SQLAlchemy моделей.

        Raises:
            SQLAlchemyError: Если произошла ошибка при получении записей.

        Usage:
            # Получение всех пользователей
            statement = select(User)
            users = await data_manager.get_all(statement)

            # Получение всех активных пользователей, отсортированных по имени
            statement = select(User).where(User.is_active == True).order_by(User.username)
            active_users = await data_manager.get_all(statement)
        """
        try:
            result = await self.session.execute(select_statement)
            return list(result.unique().scalars().all())
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при получении записей: %s", e)
            return []

    async def update_one(self, model_to_update: M, updated_model: Any = None) -> M:
        """
        Обновляет одну запись в базе данных.

        Args:
            model_to_update (M): Модель SQLAlchemy для обновления.
            updated_model (Any): Объект с новыми данными.

        Returns:
            M: Обновленная SQLAlchemy модель или None, если запись не найдена.

        Raises:
            SQLAlchemyError: Если произошла ошибка при обновлении.

        Usage:
            # Получение и обновление пользователя
            statement = select(User).where(User.id == user_id)
            found_user = await data_manager.get_one(statement)

            # Простое обновление атрибутов
            found_user.username = "new_username"
            updated_user = await data_manager.update_one(found_user)

            # Обновление с использованием другой модели
            updated_data = UserUpdate(username="new_username", email="new@example.com")
            updated_user = await data_manager.update_one(found_user, updated_data)
        """
        try:
            if not model_to_update:
                raise ValueError("Модель для обновления не предоставлена")

            if updated_model:
                for key, value in updated_model.to_dict().items():
                    if key != "id":
                        setattr(model_to_update, key, value)

            await self.session.commit()
            await self.session.refresh(model_to_update)
            return model_to_update
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при обновлении: %s", e)
            raise

    async def update_some(self, model: M, fields: dict) -> M:
        """
        Обновляет указанные поля модели.

        Args:
            model (M): Модель SQLAlchemy для обновления
            fields (dict): Словарь полей для обновления {field_name: new_value}

        Returns:
            M: Обновленная модель SQLAlchemy

        Raises:
            SQLAlchemyError: Если произошла ошибка при обновлении полей

        Usage:
            # Получение пользователя
            statement = select(User).where(User.id == user_id)
            user = await data_manager.get_one(statement)

            # Обновление нескольких полей
            updated_user = await data_manager.update_some(user, {
                "username": "new_username",
                "email": "new@example.com",
                "is_active": True
            })

            # Обновление одного поля
            updated_user = await data_manager.update_some(user, {"last_login": datetime.now()})
        """
        try:
            for field, value in fields.items():
                setattr(model, field, value)

            await self.session.commit()
            await self.session.refresh(model)
            return model
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при обновлении полей: %s", e)
            raise

    async def delete_one(self, delete_statement: Executable) -> bool:
        """
        Удаляет одну запись или несколько записей из базы данных.

        Args:
            delete_statement (Executable): SQL-запрос для удаления.

        Returns:
            bool: True, если запись(и) удалена(ы), False в противном случае.

        Raises:
            SQLAlchemyError: Если произошла ошибка при удалении.

        Usage:
            # Удаление пользователя по ID
            statement = delete(User).where(User.id == user_id)
            success = await data_manager.delete_one(statement)

            # Удаление всех неактивных пользователей
            statement = delete(User).where(User.is_active == False)
            success = await data_manager.delete_one(statement)
        """
        try:
            self.logger.debug("SQL запрос на удаление: %s", delete_statement)
            await self.session.execute(delete_statement)
            await self.session.flush()
            await self.session.commit()
            self.logger.info("Запись успешно удалена")
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при удалении: %s", e)
            return False

    async def exists(self, select_statement: Executable) -> bool:
        """
        Проверяет, существует ли хотя бы одна запись на основе предоставленного SQL-запроса.

        Args:
            select_statement (Executable): SQL-запрос для выборки.

        Returns:
            bool: True, если запись существует, иначе False.

        Usage:
            # Проверка существования пользователя с определенным email
            statement = select(User).where(User.email == "test@example.com")
            exists = await data_manager.exists(statement)

            # Проверка существования активных администраторов
            statement = select(User).where(and_(User.is_active == True, User.role == "admin"))
            has_active_admins = await data_manager.exists(statement)

            # Проверка существования заказа с определенным номером
            statement = select(Order).where(Order.order_number == "ORD123")
            has_order_with_number = await data_manager.exists(statement)
        """
        try:
            result = await self.session.execute(select_statement)
            return result.scalar() is not None
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при проверке существования: %s", e)
            return False

    async def count(self, select_statement: Optional[Select] = None) -> int:
        """
        Подсчитывает количество записей, соответствующих запросу.

        Args:
            select_statement (Executable, optional): SQL-запрос для выборки.
                Если None, подсчитываются все записи.

        Returns:
            int: Количество записей.

        Example:
            # Подсчет всех пользователей
            total_users = await data_manager.count()

            # Подсчет активных пользователей
            statement = select(User).where(User.is_active == True)
            active_users_count = await data_manager.count(statement)
        """
        try:
            if select_statement is None:
                select_statement = select(self.model)

            count_query = select(func.count()).select_from(select_statement.subquery())
            result = await self.session.execute(count_query)
            return result.scalar() or 0
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при подсчете записей: %s", e)
            return 0

    async def bulk_create(self, models: List[M]) -> List[M]:
        """
        Массовое создание записей в базе данных.

        Args:
            models (List[M]): Список моделей для добавления.

        Returns:
            List[T]: Список добавленных записей в виде схем.

        Raises:
            SQLAlchemyError: Если произошла ошибка при массовом добавлении.

        Example:
            # Создание нескольких пользователей
            users = [
                User(username="user1", email="user1@example.com"),
                User(username="user2", email="user2@example.com"),
                User(username="user3", email="user3@example.com")
            ]
            created_users = await data_manager.bulk_create(users)
        """
        try:
            self.session.add_all(models)
            await self.session.commit()

            # Обновляем модели, чтобы получить ID и другие автогенерируемые поля
            for model in models:
                await self.session.refresh(model)

            return models
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при массовом добавлении: %s", e)
            raise

    async def bulk_update(self, models: List[M]) -> List[M]:
        """
        Массовое обновление записей в базе данных.

        Args:
            models (List[M]): Список моделей для обновления.

        Returns:
            List[M]: Список обновленных моделей.

        Raises:
            SQLAlchemyError: Если произошла ошибка при массовом обновлении.

        Example:
            # Получение всех неактивных пользователей
            statement = select(User).where(User.is_active == False)
            inactive_users = await data_manager.get_all(statement)

            # Активация всех неактивных пользователей
            for user in inactive_users:
                user.is_active = True

            updated_users = await data_manager.bulk_update(inactive_users)
        """
        try:
            await self.session.commit()

            # Обновляем модели
            for model in models:
                await self.session.refresh(model)

            return models
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при массовом обновлении: %s", e)
            raise

    async def get_or_create(
        self, filters: dict, defaults: Optional[dict] = None
    ) -> Tuple[M, bool]:
        """
        Получает запись по фильтрам или создает новую, если она не существует.

        Args:
            filters (dict): Словарь фильтров для поиска записи.
            defaults (dict, optional): Словарь значений по умолчанию для новой записи.

        Returns:
            Tuple[M, bool]: Кортеж (модель, создана), где создана=True, если запись была создана.

        Raises:
            SQLAlchemyError: Если произошла ошибка при получении или создании записи.

        Example:
            # Получение или создание пользователя по email
            user, created = await data_manager.get_or_create(
                {"email": "test@example.com"},
                {"username": "test_user", "is_active": True}
            )

            if created:
                print("Пользователь создан")
            else:
                print("Пользователь уже существует")
        """
        try:
            # Создаем условия для поиска
            conditions = []
            for field, value in filters.items():
                conditions.append(getattr(self.model, field) == value)

            # Ищем запись
            statement = select(self.model).where(and_(*conditions))
            instance = await self.get_one(statement)

            if instance:
                return instance, False

            # Создаем новую запись
            create_data = {**filters}
            if defaults:
                create_data.update(defaults)

            new_instance = self.model(**create_data)
            self.session.add(new_instance)
            await self.session.commit()
            await self.session.refresh(new_instance)

            return new_instance, True
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при получении или создании записи: %s", e)
            raise

    async def update_or_create(self, filters: dict, defaults: dict) -> Tuple[M, bool]:
        """
        Обновляет запись по фильтрам или создает новую, если она не существует.

        Args:
            filters (dict): Словарь фильтров для поиска записи.
            defaults (dict): Словарь значений для обновления или создания.

        Returns:
            Tuple[M, bool]: Кортеж (модель, создана), где создана=True, если запись была создана.

        Raises:
        SQLAlchemyError: Если произошла ошибка при обновлении или создании записи.

        Example:
            # Обновление или создание настроек пользователя
            settings, created = await data_manager.update_or_create(
                {"user_id": user_id},
                {"theme": "dark", "notifications_enabled": True}
            )

            if created:
                print("Настройки созданы")
            else:
                print("Настройки обновлены")
        """
        try:
            # Создаем условия для поиска
            conditions = []
            for field, value in filters.items():
                conditions.append(getattr(self.model, field) == value)

            # Ищем запись
            statement = select(self.model).where(and_(*conditions))
            instance = await self.get_one(statement)

            if instance:
                # Обновляем существующую запись
                for field, value in defaults.items():
                    setattr(instance, field, value)

                await self.session.commit()
                await self.session.refresh(instance)
                return instance, False

            # Создаем новую запись
            create_data = {**filters, **defaults}
            new_instance = self.model(**create_data)
            self.session.add(new_instance)
            await self.session.commit()
            await self.session.refresh(new_instance)

            return new_instance, True
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при обновлении или создании записи: %s", e)
            raise

    async def filter_by(self, **kwargs) -> List[M]:
        """
        Фильтрует записи по указанным параметрам.

        Операторы фильтрации:
        | Оператор  | Описание                               | Пример использования           |
        |-----------|----------------------------------------|--------------------------------|
        | eq        | Равно (=)                              | field__eq=value                |
        | ne        | Не равно (!=)                          | field__ne=value                |
        | gt        | Больше (>)                             | field__gt=value                |
        | lt        | Меньше (<)                             | field__lt=value                |
        | gte       | Больше или равно (>=)                  | field__gte=value               |
        | lte       | Меньше или равно (<=)                  | field__lte=value               |
        | in        | В списке                               | field__in=[value1, value2]     |
        | not_in    | Не в списке                            | field__not_in=[value1, value2] |
        | like      | LIKE (с учетом регистра)               | field__like="%value%"          |
        | ilike     | ILIKE (без учета регистра)             | field__ilike="%value%"         |
        | is_null   | IS NULL (True) или IS NOT NULL (False) | field__is_null=True            |

        Примечание:
        - Если оператор не указан (просто field=value), используется оператор равенства (=)
        - Для строковых поисков с LIKE/ILIKE используйте % как символ подстановки

        Args:
            **kwargs: Параметры фильтрации в формате field=value.

        Returns:
            List[M]: Список отфильтрованных записей.

        Example:
            # Простая фильтрация по равенству
            users = await data_manager.filter_by(is_active=True, role="admin")

            # Фильтрация с использованием операторов
            users = await data_manager.filter_by(
                age__gte=18,                      # Возраст >= 18
                email__ilike="%@example.com",     # Email заканчивается на @example.com
                role__in=["admin", "moderator"],  # Роль - admin или moderator
                deleted_at__is_null=True          # Не удаленные записи
            )

            # Комбинирование простых и сложных фильтров
            products = await data_manager.filter_by(
                category="electronics",           # Категория равна electronics
                price__lt=1000,                   # Цена < 1000
                name__ilike="%phone%"             # Название содержит "phone" (без учета регистра)
            )
        """
        try:
            conditions = []

            for key, value in kwargs.items():
                if "__" in key:
                    field, operator = key.split("__", 1)
                    column = getattr(self.model, field)

                    if operator == "eq":
                        conditions.append(column == value)
                    elif operator == "ne":
                        conditions.append(column != value)
                    elif operator == "gt":
                        conditions.append(column > value)
                    elif operator == "lt":
                        conditions.append(column < value)
                    elif operator == "gte":
                        conditions.append(column >= value)
                    elif operator == "lte":
                        conditions.append(column <= value)
                    elif operator == "in":
                        conditions.append(column.in_(value))
                    elif operator == "not_in":
                        conditions.append(~column.in_(value))
                    elif operator == "like":
                        conditions.append(column.like(value))
                    elif operator == "ilike":
                        conditions.append(column.ilike(value))
                    elif operator == "is_null":
                        if value:
                            conditions.append(column.is_(None))
                        else:
                            conditions.append(column.is_not(None))
                else:
                    conditions.append(getattr(self.model, key) == value)

            statement = select(self.model).where(and_(*conditions))
            return await self.get_all(statement)
        except (SQLAlchemyError, AttributeError) as e:
            self.logger.error("❌ Ошибка при фильтрации записей: %s", e)
            return []

    async def execute_raw_query(self, query: str, params: Optional[dict] = None) -> Any:
        """
        Выполняет произвольный SQL-запрос.

        Args:
            query (str): SQL-запрос.
            params (dict, optional): Параметры запроса.

        Returns:
            Any: Результат выполнения запроса.

        Example:
            # Выполнение сложного запроса с агрегацией
            result = await data_manager.execute_raw_query(
                "SELECT role, COUNT(*) as count FROM users GROUP BY role",
            )

            # Выполнение запроса с параметрами
            result = await data_manager.execute_raw_query(
                "SELECT * FROM users WHERE email LIKE :email_pattern",
                {"email_pattern": "%@example.com"}
            )
        """
        try:
            result = await self.session.execute(text(query), params or {})
            return result
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при выполнении произвольного запроса: %s", e)
            raise


class BaseEntityManager(BaseDataManager[T]):
    """Базовый менеджер для работы с сущностями.

    Предоставляет базовые CRUD операции для всех типов сущностей.

    Attributes:
        session: Сессия базы данных SQLAlchemy
        schema: Класс Pydantic схемы для валидации
        model: Класс SQLAlchemy модели
    """

    def __init__(self, session, schema: Type[T], model: Type[M]):
        """
        Инициализирует менеджер.

        Args:
            session: Сессия базы данных SQLAlchemy
            schema: Класс Pydantic схемы для валидации данных
            model: Класс SQLAlchemy модели
        """
        super().__init__(session, schema, model)

    async def add_item(self, model: M) -> T:
        """
        Добавляет одну запись в базу данных и возвращает её в виде схемы.

        Args:
            model (M): Модель SQLAlchemy для добавления.

        Returns:
            T: Добавленная запись в виде схемы Pydantic.

        Raises:
            SQLAlchemyError: Если произошла ошибка при добавлении.

        Example:
            # Создание новой модели и добавление её в БД
            new_user = User(username="john_doe", email="john@example.com")
            user_schema = await data_manager.add_item(new_user)
        """
        model_instance = await self.add_one(model)
        return self.schema.model_validate(model_instance)

    async def get_item(self, item_id: int) -> T | None:
        """
        Получает элемент по ID и преобразует его в схему

        Args:
            item_id: ID элемента для получения

        Returns:
            T | None: Найденный объект в виде схемы Pydantic или None
        """
        statement = select(self.model).where(self.model.id == item_id)
        model_instance = await self.get_one(statement)
        if model_instance is None:
            return None
        return self.schema.model_validate(model_instance)

    async def get_item_by_field(self, field: str, value: Any) -> Optional[T]:
        """
        Получает запись по значению поля и преобразует её в схему.

        Args:
            field: Имя поля
            value: Значение поля

        Returns:
            T | None: Найденная запись в виде схемы или None
        """
        statement = select(self.model).where(getattr(self.model, field) == value)
        model_instance = await self.get_one(statement)

        if model_instance is None:
            return None

        return self.schema.model_validate(model_instance)

    async def get_model_by_field(self, field: str, value: Any) -> Optional[M]:
        """
        Получает запись по значению поля в виде модели базы данных.

        Args:
            field: Имя поля
            value: Значение поля

        Returns:
            M | None: Найденная запись в виде модели базы данных или None
        """
        statement = select(self.model).where(getattr(self.model, field) == value)
        return await self.get_one(statement)

    async def get_items(
        self,
        statement: Optional[Executable] = None,
        schema: Optional[Type[T]] = None,
        transform_func: Optional[Callable[[M], Any]] = None,
    ) -> List[T]:
        """
        Получает список элементов и преобразует их в схемы.

        Args:
            statement: SQL выражение для выборки (если None, выбираются все записи)
            schema: Класс схемы для сериализации (если None, используется self.schema)
            transform_func: Функция для преобразования данных перед валидацией схемы

        Returns:
            List[T]: Список объектов в виде схем Pydantic
        """
        if statement is None:
            statement = select(self.model)

        models = await self.get_all(statement)
        schema_to_use = schema or self.schema

        if transform_func:
            models = [transform_func(model) for model in models]

        return [schema_to_use.model_validate(model) for model in models]

    async def get_paginated_items(
        self,
        select_statement: Select,
        pagination: PaginationParams,
        schema: Optional[Type[T]] = None,
        transform_func: Optional[Callable[[M], Any]] = None,
    ) -> tuple[List[T], int]:
        """
        Получает пагинированные записи из базы данных и преобразует их в схемы.

        Args:
            select_statement (Optional[Select] = None): SQL-запрос для выборки.
            pagination (PaginationParams): Параметры пагинации.
            schema: Опциональная схема для сериализации (если None, используется self.schema)
            transform_func: Опциональная функция для преобразования данных перед валидацией схемы

        Returns:
            tuple[List[T], int]: Список пагинированных записей в виде схем и общее количество записей.

        Raises:
            SQLAlchemyError: Если произошла ошибка при получении пагинированных записей.
        """
        try:
            # Получаем общее количество записей
            total = (
                await self.session.scalar(
                    select(func.count()).select_from(select_statement.subquery())
                )
                or 0
            )

            # Применяем сортировку
            sort_column = getattr(self.model, pagination.sort_by)
            select_statement = select_statement.order_by(
                desc(sort_column) if pagination.sort_desc else asc(sort_column)
            )

            # Применяем пагинацию
            select_statement = select_statement.offset(pagination.skip).limit(
                pagination.limit
            )

            # Получаем модели
            models: List[M] = await self.get_all(select_statement)

            # Преобразуем модели в схемы
            schema_to_use = schema or self.schema
            items = []

            for model in models:
                if transform_func:
                    model = transform_func(model)
                items.append(schema_to_use.model_validate(model))

            return items, total
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при получении пагинированных записей: %s", e)
            return items, total

    async def update_item(self, item_id: int, updated_item: T) -> T:
        """
        Обновляет элемент по ID и возвращает схему.

        Args:
            item_id: ID элемента для обновления
            updated_item: Новые данные элемента

        Returns:
            T: Обновленный объект в виде схемы Pydantic

        Raises:
            ValueError: Если элемент с указанным ID не найден
        """
        # Получаем модель из БД
        statement = select(self.model).where(self.model.id == item_id)
        model_instance = await self.get_one(statement)

        if not model_instance:
            raise ValueError(f"Элемент с ID {item_id} не найден")

        # Обновляем модель
        updated_model = await self.update_one(model_instance, updated_item)

        # Преобразуем модель в схему
        return self.schema.model_validate(updated_model)

    async def update_items(self, item_id: int, fields: dict) -> T:
        """
        Обновляет указанные поля записи и возвращает обновленную схему.

        Args:
            item_id: ID записи
            fields: Словарь полей для обновления {field_name: new_value}

        Returns:
            T: Обновленная схема Pydantic

        Raises:
            ValueError: Если элемент с указанным ID не найден

        Usage:
            # Обновление нескольких полей
            updated_user = await update_items(1, {"name": "Новое имя", "email": "new@example.com", "is_active": True})
        """
        # Получаем модель из БД
        statement = select(self.model).where(self.model.id == item_id)
        model = await self.get_one(statement)

        if not model:
            raise ValueError(f"Элемент с ID {item_id} не найден")

        # Обновляем поля модели
        updated_model = await self.update_some(model, fields)

        # Преобразуем модель в схему
        return self.schema.model_validate(updated_model)

    async def delete_item(self, item_id: int) -> bool:
        """
        Удаляет элемент по ID.

        Args:
            item_id: ID элемента для удаления

        Returns:
            bool: True если успешно удален
        """
        statement = delete(self.model).where(self.model.id == item_id)
        return await self.delete_one(statement)

    async def delete_items(self) -> bool:
        """
        Удаляет все элементы.

        Returns:
            bool: True если успешно удалены
        """
        statement = delete(self.model)
        return await self.delete_one(statement)

    async def search_items(self, q: str, fields: Optional[List[str]] = None) -> List[T]:
        """
        Поиск элементов по подстроке в указанных полях.

        Args:
            q: Строка для поиска
            fields: Список полей для поиска. Если None, используются поля 'title' или 'name'

        Returns:
            List[T]: Список найденных объектов в виде схем

        Raises:
            AttributeError: Если модель не имеет указанных атрибутов или стандартных (title/name)
        """
        # Если поля не указаны, используем стандартные
        if fields is None:
            if hasattr(self.model, "title"):
                fields = ["title"]
            elif hasattr(self.model, "name"):
                fields = ["name"]
            else:
                raise AttributeError(
                    "Модель не имеет атрибута 'title' или 'name'. Укажите поля для поиска явно."
                )

        # Проверяем, что все указанные поля существуют
        invalid_fields = [field for field in fields if not hasattr(self.model, field)]
        if invalid_fields:
            raise AttributeError(
                f"Модель не имеет следующих атрибутов: {', '.join(invalid_fields)}"
            )

        # Создаем условие OR для поиска по всем указанным полям
        conditions = []
        for field in fields:
            conditions.append(getattr(self.model, field).ilike(f"%{q}%"))

        # Если условий нет, возвращаем пустой список
        if not conditions:
            return []

        # Создаем запрос с условием OR
        statement = select(self.model).where(or_(*conditions))

        return await self.get_items(statement)

    async def item_exists(self, item_id: int) -> bool:
        """
        Проверяет существование элемента по ID.

        Args:
            item_id: ID элемента для проверки

        Returns:
            bool: True если элемент существует, иначе False
        """
        statement = select(self.model).where(self.model.id == item_id)
        return await self.exists(statement)

    async def bulk_create_items(self, models: List[M]) -> List[T]:
        """
        Массовое создание записей в базе данных и возврат их в виде схем.

        Args:
            models (List[M]): Список моделей SQLAlchemy для добавления.

        Returns:
            List[T]: Список добавленных записей в виде схем Pydantic.

        Raises:
            SQLAlchemyError: Если произошла ошибка при массовом добавлении.

        Example:
            # Создание нескольких пользователей
            users = [
                User(username="user1", email="user1@example.com"),
                User(username="user2", email="user2@example.com"),
                User(username="user3", email="user3@example.com")
            ]
            created_user_schemas = await data_manager.bulk_create_items(users)
        """
        model_instances = await self.bulk_create(models)
        return [self.schema.model_validate(model) for model in model_instances]
