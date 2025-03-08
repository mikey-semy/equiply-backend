import logging
from typing import Any, Callable, Generic, List, Optional, Type, TypeVar
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import asc, delete, desc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Executable

from app.models.v1.base import BaseModel
from app.schemas.v1.base import BaseSchema
from app.schemas.v1.pagination import PaginationParams

from app.core.settings import settings

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

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)


class BaseEmailService(BaseService):
    def __init__(self):

        super().__init__()

        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.password = settings.SMTP_PASSWORD.get_secret_value()
        # Используем путь из настроек вместо вычисления
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        self.logger.debug("Директория с шаблонами: %s", template_dir)

        # Проверяем существование директории
        if not template_dir.exists():
            self.logger.error("Директория с шаблонами не найдена: %s", template_dir)
            template_dir = Path(__file__).parents[4] / 'templates' / 'mail'
            self.logger.warning("Пробуем запасной путь: %s", template_dir)

        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

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

    async def add_one(self, model: Any) -> T:
        """
        Добавляет одну запись в базу данных.

        Args:
            model (Any): Модель для добавления.

        Returns:
            T: Добавленная запись в виде схемы.

        Raises:
            SQLAlchemyError: Если произошла ошибка при добавлении.
        """
        try:
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return self.schema(**model.to_dict())
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при добавлении: %s", e)
            raise

    async def get_one(self, select_statement: Executable) -> Any | None:
        """
        Получает одну запись из базы данных.

        Args:
            select_statement (Executable): SQL-запрос для выборки.

        Returns:
            Any | None: Полученная запись или None, если запись не найдена.

        Raises:
            SQLAlchemyError: Если произошла ошибка при получении записи.
        """
        try:
            self.logger.info("Получение записи из базы данных")
            self.logger.debug("SQL-запрос: %s", select_statement)
            result = await self.session.execute(select_statement)
            return result.scalar()
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при получении записи: %s", e)
            raise

    async def get_all(
        self,
        select_statement: Executable,
        schema: Type[T] = None,
        transform_func: Optional[
            Callable
        ] = None,  # для преобразования данных перед возвратом
    ) -> List[Any]:
        """
        Получает все записи из базы данных.

        Args:
            select_statement (Executable): SQL-запрос для выборки.

        Returns:
            List[T]: Список всех записей.

        Raises:
            SQLAlchemyError: Если произошла ошибка при получении записей.
        """
        try:
            result = await self.session.execute(select_statement)
            items = result.unique().scalars().all()
            schema_to_use = schema or self.schema

            if transform_func:
                items = [transform_func(item) for item in items]

            return [schema_to_use.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при получении записей: %s", e)
            return []

    async def exists(self, select_statement: Executable) -> bool:
        """
        Проверяет, существует ли хотя бы одна запись на основе предоставленного     SQL-запроса.

        Args:
            select_statement (Executable): SQL-запрос для выборки.

        Returns:
            bool: True, если запись существует, иначе False.
        """
        try:
            result = await self.session.execute(select_statement)
            return result.scalar() is not None
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при проверке существования: %s", e)
            return False

    async def get_paginated(
        self,
        select_statement: Executable,
        pagination: PaginationParams,
        schema: Type[T] = None,
        transform_func: Optional[Callable] = None,
    ) -> tuple[List[T], int]:
        """
        Получает пагинированные записи из базы данных.

        Args:
            select_statement (Executable): SQL-запрос для выборки.
            pagination (PaginationParams): Параметры пагинации.
            schema: Опциональная схема для сериализации (если None, используется self.schema)
            transform_func: Опциональная функция для преобразования данных перед валидацией схемы
        Returns:
            tuple[List[T], int]: Список пагинированных записей и общее количество записей.

        Raises:
            SQLAlchemyError: Если произошла ошибка при получении пагинированных записей.
        """
        try:
            total = await self.session.scalar(
                select(func.count()).select_from(select_statement)
            )

            sort_column = getattr(self.model, pagination.sort_by)

            select_statement = select_statement.order_by(
                desc(sort_column) if pagination.sort_desc else asc(sort_column)
            )

            select_statement = select_statement.offset(pagination.skip).limit(
                pagination.limit
            )

            items = await self.get_all(
                select_statement,
                schema=schema or self.schema,
                transform_func=transform_func,
            )

            return items, total
        except SQLAlchemyError as e:
            self.logger.error("❌ Ошибка при получении пагинированных записей: %s", e)
            return [], 0

    async def delete(self, delete_statement: Executable) -> bool:
        """
        Удаляет одну запись или несколько записей из базы данных.

        Args:
            delete_statement (Executable): SQL-запрос для удаления.

        Returns:
            bool: True, если запись(и) удалена(ы), False в противном случае.

        Raises:
            SQLAlchemyError: Если произошла ошибка при удалении.
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

    async def update_one(self, model_to_update, updated_model: Any = None) -> T | None:
        """
        Обновляет одну запись в базе данных.

        Args:
            model_to_update: Модель для обновления.
            updated_model (Any): Обновленная модель.

        Returns:
            T | None: Обновленная запись в виде схемы или None, если запись не найдена.

        Raises:
            SQLAlchemyError: Если произошла ошибка при обновлении.

        Usage:
            # Для простых обновлений
            # (например, обновление только одного поля в менеджере данных)
            await self.update_one(found_test)

            # Для сложных обновлений с новыми данными
            await self.update_one(found_test, updated_test)
        """
        try:
            if not model_to_update:
                return None

            if updated_model:
                for key, value in updated_model.to_dict().items():
                    if key != "id":
                        setattr(model_to_update, key, value)

            await self.session.commit()
            await self.session.refresh(model_to_update)
            return self.schema(**model_to_update.to_dict())
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при обновлении: %s", e)
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
        self.model = model

    async def add_item(self, new_item) -> T:
        """
        Добавляет новый элемент в базу данных.

        Args:
            new_item: Объект для добавления в БД

        Returns:
            T: Добавленный объект в виде схемы
        """
        return await self.add_one(new_item)

    async def get_item(self, item_id: int) -> T | None:
        """
        Получает элемент по ID.

        Args:
            item_id: ID элемента для получения

        Returns:
            T | None: Найденный объект или None
        """
        statement = select(self.model).where(self.model.id == item_id)
        schema: T = await self.get_one(statement)
        return schema

    async def get_items(self, statement=None) -> List[T]:
        """
        Получает список элементов.

        Args:
            statement: SQL выражение для выборки (опционально)

        Returns:
            List[T]: Список объектов в виде схем
        """
        if statement is None:
            statement = select(self.model)
        schemas: List[T] = []
        models = await self.get_all(statement)
        for model in models:
            schemas.append(model)
        return schemas

    async def get_user_by_field(self, field: str, value: Any) -> Optional[T]:
        """
        Получает запись по значению поля

        Args:
            field: Имя поля
            value: Значение поля

        Returns:
            T | None: Найденная запись или None
        """
        statement = select(self.model).where(getattr(self.model, field) == value)
        return await self.get_one(statement)

    async def get_user_by_email(self, email: str) -> Any | None:
        """
        Получает элемент по email.

        Args:
            email: Email для поиска

        Returns:
            Any | None: Найденный объект или None
        """
        statement = select(self.model).where(self.model.email == email)
        result = await self.session.execute(statement)
        return result.unique().scalar_one_or_none()

    async def search_items(self, q: str) -> List[T]:
        """
        Поиск элементов по подстроке.

        Args:
            q: Строка для поиска

        Returns:
            List[T]: Список найденных объектов

        Raises:
            AttributeError: Если модель не имеет атрибутов title/name
        """
        if hasattr(M, "title"):
            statement = select(self.model).where(self.model.title.ilike(f"%{q}%"))
        elif hasattr(M, "name"):
            statement = select(self.model).where(self.model.name.ilike(f"%{q}%"))
        else:
            raise AttributeError("Модель не имеет атрибута 'title' или 'name'.")
        return await self.get_items(statement)

    async def update_item(self, item_id: int, updated_item: T) -> T | None:
        """
        Обновляет элемент по ID.

        Args:
            item_id: ID элемента для обновления
            updated_item: Новые данные элемента

        Returns:
            T | None: Обновленный объект или None
        """
        old_item = await self.get_item(item_id)
        schema: T = await self.update_one(old_item, updated_item)
        return schema

    async def update_fields(self, item_id: int, fields: dict) -> bool:
        """
        Обновляет указанные поля записи.

        Args:
            item_id: ID записи
            fields: Словарь полей для обновления {field_name: new_value}

        Returns:
            bool: True если успешно обновлено
        """
        try:
            item = await self.get_item(item_id)
            if not item:
                return False

            for field, value in fields.items():
                setattr(item, field, value)

            await self.session.commit()
            return True

        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("❌ Ошибка при обновлении полей: %s", e)
            return False

    async def delete_item(self, item_id: int) -> bool:
        """
        Удаляет элемент по ID.

        Args:
            item_id: ID элемента для удаления

        Returns:
            bool: True если успешно удален
        """
        statement = delete(self.model).where(self.model.id == item_id)
        return await self.delete(statement)

    async def delete_items(self) -> bool:
        """
        Удаляет все элементы.

        Returns:
            bool: True если успешно удалены
        """
        statement = delete(self.model)
        return await self.delete(statement)
