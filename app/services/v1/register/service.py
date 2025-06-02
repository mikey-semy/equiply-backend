from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (TokenExpiredError, TokenInvalidError,
                                 UserCreationError, UserExistsError,
                                 UserNotFoundError)
from app.core.integrations.mail import AuthEmailDataManager
from app.core.security import PasswordHasher, TokenManager
from app.models import UserModel
from app.schemas import (OAuthUserSchema, RegistrationResponseSchema,
                         RegistrationSchema, UserCredentialsSchema, UserRole,
                         VerificationResponseSchema)
from app.services.v1.base import BaseService

from .data_manager import RegisterDataManager


class RegisterService(BaseService):
    """
    Сервис для регистрации пользователей.

    Этот класс предоставляет методы для регистрации пользователей,
    включая верификацию email.

    Attributes:
        session: Асинхронная сессия для работы с базой данных.

    Methods:
        create_user: Создание пользователя.
        _create_user_internal: Внутренний метод создания пользователя в базе данных.
        generate_verification_token: Генерирует токен для подтверждения email
        verify_email: Подтверждает email пользователя
        resend_verification_email: Повторно отправляет письмо для подтверждения email
        check_verification_status: Проверяет статус верификации email пользователя
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.data_manager = RegisterDataManager(session)
        self.email_data_manager = AuthEmailDataManager()

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

        await self.email_data_manager.send_verification_email(
            to_email=created_user.email,
            user_name=created_user.username,
            verification_token=verification_token,
        )

        return RegistrationResponseSchema(
            user_id=created_user.id, email=created_user.email
        )

    async def create_oauth_user(self, user: OAuthUserSchema) -> UserCredentialsSchema:
        """
        Создает нового пользователя через OAuth аутентификацию.

        Args:
            user: Данные пользователя от OAuth провайдера

        Returns:
            UserCredentialsSchema: Учетные данные пользователя
        """
        created_user = await self._create_user_internal(user)

        self.logger.debug(
            "Созданный пользователь (created_user): %s", vars(created_user)
        )

        return created_user

    async def _create_user_internal(
        self, user: OAuthUserSchema | RegistrationSchema
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

        # OAuth: Преобразуем в OAuthUserSchema если есть OAuth идентификаторы
        user_dict = user.model_dump()

        self.logger.debug("Данные пользователя перед созданием: %s", user_dict)

        user = OAuthUserSchema(**user_dict)

        # Проверка username
        existing_user = await self.data_manager.get_item_by_field(
            "username", user.username
        )
        if existing_user:
            self.logger.error(
                "Пользователь с username '%s' уже существует", user.username
            )
            raise UserExistsError("username", user.username)

        # Проверка email
        existing_user = await self.data_manager.get_item_by_field("email", user.email)
        if existing_user:
            self.logger.error("Пользователь с email '%s' уже существует", user.email)
            raise UserExistsError("email", user.email)

        # Проверяем телефон только для обычной регистрации
        if isinstance(user, RegistrationSchema) and user.phone:
            existing_user = await self.data_manager.get_item_by_field(
                "phone", user.phone
            )
            if existing_user:
                self.logger.error(
                    "Пользователь с телефоном '%s' уже существует", user.phone
                )
                raise UserExistsError("phone", user.phone)

        # OAuth: Создаем модель пользователя
        user_data = user.to_dict()
        vk_id = user_data.get("vk_id")
        google_id = user_data.get("google_id")
        yandex_id = user_data.get("yandex_id")
        avatar = user_data.get("avatar")

        # Устанавливаем идентификаторы провайдеров, если они есть
        user_model = UserModel(
            username=user.username,
            email=user.email,
            phone=user.phone,
            hashed_password=PasswordHasher.hash_password(user.password),
            role=UserRole.USER,
            # OAuth:
            avatar=avatar,
            vk_id=int(vk_id) if vk_id is not None else None,
            google_id=str(google_id) if google_id is not None else None,
            yandex_id=int(yandex_id) if yandex_id is not None else None,
        )

        try:
            created_user = await self.data_manager.add_user(user_model)

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
        from app.core.settings import settings

        expires_at = int(datetime.now(timezone.utc).timestamp()) + (
            settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60
        )
        payload = {
            "sub": str(user_id),
            "type": "email_verification",
            "expires_at": expires_at,
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
            user_id = int(payload["sub"])

            # Проверяем тип токена
            if payload.get("type") != "email_verification":
                raise TokenInvalidError()

            # Проверяем срок действия токена
            expires_at = payload.get("expires_at")
            if TokenManager.is_expired(expires_at):
                raise TokenExpiredError()

            user = await self.data_manager.get_item_by_field("id", user_id)
            if not user:
                raise UserNotFoundError(field="id", value=user_id)

            # Если пользователь уже верифицирован, просто возвращаем успех
            if user.is_verified:
                return VerificationResponseSchema(
                    user_id=user_id,
                    success=True,
                    message="Email уже был подтвержден ранее.",
                )

            await self.data_manager.update_items(user_id, {"is_verified": True})

            # Отправляем письмо об успешной регистрации
            try:
                await self.email_data_manager.send_registration_success_email(
                    to_email=user.email, user_name=user.username
                )
                self.logger.info(
                    "Отправлено письмо об успешной регистрации",
                    extra={"user_id": user_id, "email": user.email},
                )
            except Exception as e:
                # Не прерываем процесс верификации, если письмо не отправилось
                self.logger.error(
                    "Ошибка при отправке письма об успешной регистрации: %s",
                    e,
                    extra={"user_id": user_id, "email": user.email},
                )

            return VerificationResponseSchema(
                user_id=user_id,
                success=True,
                message="Email успешно подтвержден. Теперь вы можете войти в систему.",
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.error("Ошибка верификации токена: %s", e)
            raise

    async def resend_verification_email(self, email: str) -> None:
        """
        Повторно отправляет письмо для подтверждения email

        Args:
            email: Email пользователя

        Raises:
            UserNotFoundError: Если пользователь с указанным email не найден
        """
        user = await self.data_manager.get_item_by_field("email", email)
        if not user:
            self.logger.error("Пользователь с email '%s' не найден", email)
            raise UserNotFoundError(field="email", value=email)

        # Проверяем, не подтвержден ли уже email
        if user.is_verified:
            self.logger.info(
                "Email уже подтвержден, новое письмо не отправлено",
                extra={"user_id": user.id, "email": user.email},
            )
            return

        verification_token = self.generate_verification_token(user.id)

        await self.email_data_manager.send_verification_email(
            to_email=user.email,
            user_name=user.username,
            verification_token=verification_token,
        )

        self.logger.info(
            "Повторно отправлено письмо для подтверждения email",
            extra={"user_id": user.id, "email": user.email},
        )

    async def check_verification_status(self, email: str) -> bool:
        """
        Проверяет статус верификации email пользователя

        Args:
            email: Email пользователя

        Returns:
            bool: True если email подтвержден, иначе False

        Raises:
            UserNotFoundError: Если пользователь с указанным email не найден
        """
        user = await self.data_manager.get_item_by_field("email", email)
        if not user:
            self.logger.error("Пользователь с email '%s' не найден", email)
            raise UserNotFoundError(field="email", value=email)

        return user.is_verified
