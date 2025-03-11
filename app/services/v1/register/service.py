from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (UserCreationError, UserExistsError,
                                 UserNotFoundError, TokenInvalidError, TokenExpiredError)
from app.core.security import PasswordHasher, TokenManager
from app.models import UserModel
from app.schemas import (RegistrationResponseSchema, VerificationResponseSchema, RegistrationSchema, UserCredentialsSchema, UserRole)
from app.services.v1.base import BaseService
from app.core.integrations.mail import AuthEmailService
from .data_manager import RegisterDataManager


class RegisterService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._data_manager = RegisterDataManager(session)
        self._email_service = AuthEmailService()

    async def create_user(self, user: RegistrationSchema) -> RegistrationResponseSchema:
        """
        Создает нового пользователя через веб-форму регистрации.

        Args:
            user: Данные пользователя из формы регистрации

        Returns:
            RegistrationResponseSchema: Схема ответа с id, email и сообщением об успехе
        """


        created_user = await self._create_user_internal(user)

        verification_token = self.generate_verification_token(created_user.id)

        await self._email_service.send_verification_email(
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
         # Проверка username
        existing_user = await self._data_manager.get_item_by_field("username", user.username)
        if existing_user:
            self.logger.error("Пользователь с username '%s' уже существует", user.username)
            raise UserExistsError("username", user.username)

        # Проверка email
        existing_user = await self._data_manager.get_item_by_field("email", user.email)
        if existing_user:
            self.logger.error("Пользователь с email '%s' уже существует", user.email)
            raise UserExistsError("email", user.email)

        # Проверяем телефон только для обычной регистрации
        if isinstance(user, RegistrationSchema) and user.phone:
            existing_user = await self._data_manager.get_item_by_field("phone", user.phone)
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
            created_user = await self._data_manager.add_user(user_model)

            user_credentials = UserCredentialsSchema(
                id=created_user.id,
                email=created_user.email,
                username=created_user.username,
                hashed_password=user_model.hashed_password,
                role=created_user.role,
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

    async def verify_email(self, token: str) -> VerificationResponseSchema:
        """
        Подтверждает email пользователя

        Args:
            token: Токен для подтверждения email

        Returns:
            VerificationResponseSchema: Схема ответа при успешной верификации
        """
        try:
            payload = TokenManager.verify_token(token)
            user_id = int(payload['sub'])

            if payload.get('type') != 'email_verification':
                raise TokenInvalidError()

            user = await self._data_manager.get_item_by_field("id", user_id)
            if not user:
                raise UserNotFoundError(field="id", value=user_id)

            await self._data_manager.update_fields(
                user_id,
                {"is_verified": True}
            )
            # Отправляем письмо об успешной регистрации
            try:
                await self._email_service.send_registration_success_email(
                    to_email=user.email,
                    user_name=user.username
                )
                self.logger.info(
                    "Отправлено письмо об успешной регистрации",
                    extra={"user_id": user_id, "email": user.email}
                )
            except Exception as e:
                # Не прерываем процесс верификации, если письмо не отправилось
                self.logger.error(
                    "Ошибка при отправке письма об успешной регистрации: %s", e,
                    extra={"user_id": user_id, "email": user.email}
                )

            return VerificationResponseSchema(
                user_id=user_id,
                success=True,
                message="Email успешно подтвержден. Теперь вы можете войти в систему."
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.error("Ошибка верификации токена: %s", e)
            raise
