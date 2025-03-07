from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (UserCreationError, UserExistsError,
                                 UserNotFoundError, TokenInvalidError, TokenExpiredError)
from app.core.security import PasswordHasher, TokenManager
from app.models import UserModel
from app.schemas import (RegistrationResponseSchema,
                         RegistrationSchema, UserCredentialsSchema, UserRole)
from app.services.v1.base import BaseService

from .data_manager import UserDataManager


class RegisterService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self._data_manager = UserDataManager(session)

    async def create_user(self, user: RegistrationSchema) -> RegistrationResponseSchema:
        """
        Создает нового пользователя через веб-форму регистрации.

        Args:
            user: Данные пользователя из формы регистрации

        Returns:
            RegistrationResponseSchema: Схема ответа с id, email и сообщением об успехе
        """
        from app.services.v1.mail.service import MailService

        created_user = await self._create_user_internal(user)

        verification_token = self.generate_verification_token(created_user.id)

        email_service = MailService()

        await email_service.send_verification_email(
            to_email=created_user.email,
            user_name=created_user.username,
            verification_token=verification_token
        )

        return RegistrationResponseSchema(
            user_id=created_user.id,
            email=created_user.email,
            message="Регистрация успешно завершена",
        )

    async def _create_user_internal(
        self, user: RegistrationSchema
    ) -> UserCredentialsSchema:
        """
        Внутренний метод создания пользователя в базе данных.

        Args:
            user: Данные нового пользователя

        Returns:
            UserModel: Созданный пользователь

        Raises:
            UserExistsError: Если пользователь с таким email или телефоном уже существует
            UserCreationError: При ошибке создания пользователя

        Note:
            - Поддерживает данные как из веб-формы, так и от OAuth провайдеров
            - Проверяет уникальность email и телефона
            - Сохраняет идентификаторы OAuth провайдеров
        """
        data_manager = UserDataManager(self.session)

         # Проверка username
        existing_user = await data_manager.get_user_by_field("username", user.username)
        if existing_user:
            self.logger.error("Пользователь с username '%s' уже существует", user.username)
            raise UserExistsError("username", user.username)

        # Проверка email
        existing_user = await data_manager.get_user_by_email(user.email)
        if existing_user:
            self.logger.error("Пользователь с email '%s' уже существует", user.email)
            raise UserExistsError("email", user.email)

        # Проверяем телефон только для обычной регистрации
        if isinstance(user, RegistrationSchema) and user.phone:
            existing_user = await data_manager.get_user_by_phone(user.phone)
            if existing_user:
                self.logger.error(
                    "Пользователь с телефоном '%s' уже существует", user.phone
                )
                raise UserExistsError("phone", user.phone)

        # Устанавливаем идентификаторы провайдеров, если они есть
        user_model = UserModel(
            username=user.username,
            email=user.email,
            phone=user.phone,
            hashed_password=PasswordHasher.hash_password(user.password),
            role=UserRole.USER,
        )

        try:
            created_user = await data_manager.add_user(user_model)

            user_credentials = UserCredentialsSchema(
                id=created_user.id,
                email=created_user.email,
                username=created_user.username,
                hashed_password=user_model.hashed_password,
            )
            return user_credentials

        except Exception as e:
            self.logger.error("Ошибка при создании пользователя: %s", e)
            raise UserCreationError(
                "Не удалось создать пользователя. Пожалуйста, попробуйте позже."
            ) from e

    def generate_verification_token(self, user_id: int) -> str:
        """
        Генерирует токен для подтверждения email

        Args:
            user_id: Идентификатор пользователя

        Returns:
            str: Токен для подтверждения email
        """
        payload = {
            'sub': str(user_id),
            'type': 'email_verification',
            'expires_at': (
                int(datetime.now(timezone.utc).timestamp()) +
                TokenManager.get_token_expiration()
            )
        }
        return TokenManager.generate_token(payload)

    async def verify_email(self, token: str) -> UserCredentialsSchema:
        """
        Подтверждает email пользователя

        Args:
            token: Токен для подтверждения email

        Returns:
            UserCredentialsSchema: Данные пользователя
        """
        try:
            payload = TokenManager.verify_token(token)
            user_id = int(payload['sub'])

            if payload.get('type') != 'email_verification':
                raise TokenInvalidError()

            user = await self._data_manager.get_user_by_field("id", user_id)
            if not user:
                raise UserNotFoundError(field="id", value=user_id)

            await self._data_manager.update_fields(
                user_id,
                {"is_verified": True}
            )
            return user

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.error("Ошибка верификации токена: %s", e)
            raise
