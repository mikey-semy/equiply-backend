from typing import Optional
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserExistsError
from app.models import UserModel
from app.schemas import UserSchema
from app.services.v1.base import BaseEntityManager


class RegisterDataManager(BaseEntityManager[UserSchema]):
    """
    Менеджер данных для регистрации пользователя в БД.

    Реализует низкоуровневые операции для работы с таблицей пользователей.
    Обрабатывает исключения БД и преобразует их в доменные исключения.

    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[UserSchema]): Схема сериализации данных
        model (Type[UserModel]): Модель пользователя

    Methods:
        add_user: Добавление пользователя в БД
        get_user_by_field: Получение пользователя по полю
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def validate_user_uniqueness(
        self, username: str, email: str, phone: Optional[str] = None
    ) -> None:
        """
        Проверяет уникальность данных пользователя одним запросом.

        Args:
            username: Имя пользователя
            email: Email пользователя
            phone: Телефон пользователя (опционально)

        Raises:
            UserExistsError: Если найден дубликат
        """
        conditions = [UserModel.username == username, UserModel.email == email]

        if phone:
            conditions.append(UserModel.phone == phone)

        statement = select(UserModel).where(or_(*conditions))
        existing_user = await self.get_one(statement)

        if existing_user:
            # Определяем какое поле дублируется
            if existing_user.username == username:
                raise UserExistsError("username", username)
            elif existing_user.email == email:
                raise UserExistsError("email", email)
            elif phone and existing_user.phone == phone:
                raise UserExistsError("phone", phone)

    async def add_user(self, user: UserModel) -> UserModel:
        """
        Добавляет нового пользователя в базу данных.

        Args:
            user: Пользователь для добавления.

        Returns:
            UserCredentialsSchema: Данные пользователя.
        """
        try:
            return await self.add_one(user)
        except IntegrityError as e:
            if "users.email" in str(e):
                self.logger.error(
                    "add_user: Пользователь с email '%s' уже существует", user.email
                )
                raise UserExistsError("email", user.email) from e
            elif "users.phone" in str(e):
                self.logger.error(
                    "add_user: Пользователь с телефоном '%s' уже существует", user.phone
                )
                raise UserExistsError("phone", user.phone) from e
            else:
                self.logger.error("Ошибка при добавлении пользователя: %s", e)
                raise
