"""
Сервис регистрации пользователей.

Обеспечивает полный цикл регистрации: валидацию, создание пользователя,
отправку письма верификации и подтверждение email.

Classes:
    RegisterService: Основной сервис для регистрации пользователей
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Response
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (TokenExpiredError, TokenInvalidError,
                                 UserNotFoundError, UserCreationError)
from app.core.integrations.cache.auth import AuthRedisDataManager
from app.core.integrations.mail import AuthEmailDataManager
from app.core.security.cookie import CookieManager
from app.core.security.token import TokenManager
from app.core.security.password import PasswordHasher
from app.core.settings import settings
from app.models import UserModel, UserRole
from app.schemas import (RegistrationDataSchema, RegistrationRequestSchema,
                         RegistrationResponseSchema,
                         ResendVerificationDataSchema,
                         ResendVerificationResponseSchema,
                         UserCredentialsSchema, VerificationDataSchema,
                         VerificationResponseSchema,
                         VerificationStatusDataSchema,
                         VerificationStatusResponseSchema,
                         OAuthUserSchema)
from app.services.v1.base import BaseService
from app.services.v1.auth.service import AuthDataManager
from .data_manager import RegisterDataManager


class RegisterService(BaseService):
    """
    Сервис для регистрации и верификации пользователей.

    Основные операции:
    1. Регистрация нового пользователя
    2. Отправка письма верификации
    3. Подтверждение email по токену
    4. Повторная отправка письма верификации

    Attributes:
        session: Асинхронная сессия базы данных
        data_manager: Менеджер данных для операций с пользователями
        email_data_manager: Менеджер для отправки email
    """

    def __init__(self, session: AsyncSession, redis: Optional[Redis] = None):
        """
        Инициализирует сервис регистрации.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных
        """
        super().__init__(session)

        self.data_manager = RegisterDataManager(session)
        self.auth_data_manager = AuthDataManager(session)
        self.email_data_manager = AuthEmailDataManager()
        self.redis_data_manager = AuthRedisDataManager(redis) if redis else None

    async def create_user(
        self,
        user_data: RegistrationRequestSchema,
        response: Optional[Response] = None,
        use_cookies: bool = False,
    ) -> RegistrationResponseSchema:
        """
        Создает нового пользователя и отправляет письмо верификации.

        Полный процесс:
        1. Валидация уникальности данных
        2. Создание пользователя в БД
        3. Генерация токенов верификации и refresh токена
        4. Отправка письма верификации
        5. Сохранение токенов в Redis

        Args:
            user_data: Данные для регистрации пользователя
            response: HTTP ответ для установки куков (опционально)
            use_cookies: Использовать ли куки для хранения токенов (по умолчанию False)

        Returns:
            RegistrationResponseSchema: Данные созданного пользователя

        Raises:
            UserExistsError: Если пользователь с такими данными уже существует
            UserCreationError: При ошибке создания в БД
        """

        self.logger.info("Начало регистрации пользователя: %s", user_data.username)

        # Валидируем уникальность данных
        await self.data_manager.validate_user_uniqueness(
            username=user_data.username, email=user_data.email, phone=user_data.phone
        )

        # Создаем пользователя
        #created_user = await self.data_manager.create_user(user_data)

        created_user_schema = await self._create_user_internal(user_data)
        created_user = await self.data_manager.get_model_by_field("id", created_user_schema.id)

        # Создаем схему пользователя для токенов
        #user_schema = UserCredentialsSchema.model_validate(created_user)

        # Создаем ограниченные токены (пользователь еще не верифицирован)
        access_token = TokenManager.create_limited_token(created_user_schema)
        refresh_token = TokenManager.create_refresh_token(created_user.id)

        # Сохраняем токены в Redis
        await self._save_tokens_to_redis(created_user_schema, access_token, refresh_token)

        # Опционально устанавливаем куки
        if response and use_cookies:
            CookieManager.set_auth_cookies(response, access_token, refresh_token)
            self.logger.debug("Установлены куки с ограниченными токенами")

        # Отправляем письмо верификации
        await self._send_verification_email(created_user)

        # Формируем данные ответа
        registration_data = RegistrationDataSchema(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            role=created_user.role.value,
            is_active=created_user.is_active,
            is_verified=created_user.is_verified,
            created_at=created_user.created_at,
            access_token=None if use_cookies else access_token,
            refresh_token=None if use_cookies else refresh_token,
            token_type=settings.TOKEN_TYPE,
            requires_verification=True,
        )

        self.logger.info(
            "Пользователь зарегистрирован с ограниченными токенами: ID=%s",
            created_user.id,
        )

        return RegistrationResponseSchema(
            message="Регистрация завершена. Подтвердите email для полного доступа.",
            data=registration_data,
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
        self, user: OAuthUserSchema | RegistrationRequestSchema
    ) -> UserCredentialsSchema:
        """
        Внутренний метод создания пользователя в базе данных.

        Args:
            user: Данные нового пользователя

        Returns:
            UserCredentialsSchema: Созданный пользователь

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

        # Валидируем уникальность данных
        await self.data_manager.validate_user_uniqueness(
            username=user.username, email=user.email, phone=user.phone
        )

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
            created_user = await self.data_manager.create_user(user_model)
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

    async def _save_tokens_to_redis(
        self, user_schema: UserCredentialsSchema, access_token: str, refresh_token: str
    ) -> None:
        """
        Сохраняет токены в Redis если доступен.

        Args:
            user_schema: Схема пользователя
            access_token: Access токен
            refresh_token: Refresh токен
        """
        if not self.redis_data_manager:
            return

        try:
            # Сохраняем access токен
            await self.redis_data_manager.save_token(user_schema, access_token)

            # Сохраняем refresh токен
            await self.redis_data_manager.save_refresh_token(
                user_schema.id, refresh_token
            )

            self.logger.info(
                "Токены сохранены в Redis", extra={"user_id": user_schema.id}
            )
        except Exception as e:
            self.logger.warning(
                "Ошибка сохранения токенов в Redis: %s",
                e,
                extra={"user_id": user_schema.id},
            )

    async def verify_email(
        self, token: str, response: Optional[Response] = None, use_cookies: bool = False
    ) -> VerificationResponseSchema:
        """
        Подтверждает email пользователя и выдает полные токены.

        Процесс верификации:
        1. Валидация и декодирование токена
        2. Проверка существования пользователя
        3. Обновление статуса is_verified
        4. Выдача полных токенов доступа
        5. Отправка письма об успешной регистрации

        Args:
            token: Токен верификации из письма
            response: HTTP ответ для обновления куков (опционально)
            use_cookies: Обновить ли куки с полными токенами (по умолчанию False)

        Returns:
            VerificationResponseSchema: Результат верификации с полными токенами

        Raises:
            TokenInvalidError: Если токен недействителен
            TokenExpiredError: Если токен истек
            UserNotFoundError: Если пользователь не найден
        """
        self.logger.info("Попытка верификации email по токену")

        try:
            # Декодируем и валидируем токен
            payload = TokenManager.verify_token(token)
            user_id = TokenManager.validate_verification_token(payload)

            # Получаем пользователя
            user = await self.data_manager.get_item_by_field("id", user_id)
            if not user:
                self.logger.warning(
                    "Пользователь не найден", extra={"user_id": str(user_id)}
                )
                raise UserNotFoundError(field="id", value=user_id)

            # Проверяем, не верифицирован ли уже
            if user.is_verified:
                # Если уже верифицирован, все равно возвращаем полные токены
                user_schema = UserCredentialsSchema.model_validate(user)
                access_token = TokenManager.create_full_token(user_schema)
                refresh_token = TokenManager.create_refresh_token(user_schema.id)

                await self._save_tokens_to_redis(
                    user_schema, access_token, refresh_token
                )

                # Обновляем куки если нужно
                if response and use_cookies:
                    CookieManager.set_auth_cookies(
                        response, access_token, refresh_token
                    )

                verification_data = VerificationDataSchema(
                    id=user_id,
                    email=user_schema.email,
                    verified_at=datetime.now(timezone.utc),
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type=settings.TOKEN_TYPE,
                )

                return VerificationResponseSchema(
                    message="Email уже был подтвержден ранее", data=verification_data
                )

            # Подтверждаем email
            await self.data_manager.update_items(user_id, {"is_verified": True})

            updated_user = await self.data_manager.get_item_by_field("id", user_id)
            user_schema = UserCredentialsSchema.model_validate(updated_user)

            new_access_token = TokenManager.create_full_token(user_schema)
            new_refresh_token = TokenManager.create_refresh_token(user_id)

            # Сохраняем новые токены в Redis
            await self._save_tokens_to_redis(
                user_schema, new_access_token, new_refresh_token
            )

            # Обновляем куки с полными токенами если нужно
            if response and use_cookies:
                CookieManager.set_auth_cookies(
                    response, new_access_token, new_refresh_token
                )
                self.logger.debug("Обновлены куки с полными токенами")

            # Отправляем письмо об успешной регистрации
            await self._send_registration_success_email(user)

            self.logger.info(
                "Email верифицирован, выданы полные токены",
                extra={"user_id": str(user_id)},
            )

            verification_data = VerificationDataSchema(
                id=user_id,
                email=user.email,
                verified_at=datetime.now(timezone.utc),
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=settings.TOKEN_TYPE,
            )

            return VerificationResponseSchema(
                message="Email успешно подтвержден. Теперь вы можете войти в систему",
                data=verification_data,
            )
        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.error("Ошибка верификации токена: %s", e)
            raise

    async def resend_verification_email(self, email: str) -> dict:
        """
        Повторно отправляет письмо верификации.

        Args:
            email: Email пользователя

        Returns:
            dict: Статус операции

        Raises:
            UserNotFoundError: Если пользователь не найден
        """
        # Поиск пользователя по email
        user_model = await self.auth_data_manager.get_user_by_identifier(email)
        if not user_model:
            raise UserNotFoundError(field="email", value=email)

        # Проверка статуса
        if user_model.is_verified:
            verification_data = VerificationDataSchema(
                id=user_model.id,
                verified_at=user_model.updated_at or user_model.created_at,
                email=user_model.email,
            )
            return VerificationResponseSchema(
                message="Email уже подтвержден", data=verification_data
            )

        # Отправка письма
        await self._send_verification_email(user_model)

        resend_data = ResendVerificationDataSchema(
            email=email,
            sent_at=datetime.now(timezone.utc),
            expires_in=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60,
        )

        return ResendVerificationResponseSchema(
            message="Письмо верификации отправлено повторно", data=resend_data
        )

    async def check_verification_status(
        self, email: str
    ) -> VerificationStatusResponseSchema:
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

        status_data = VerificationStatusDataSchema(
            email=email,
            is_verified=user.is_verified,
            checked_at=datetime.now(timezone.utc),
        )

        return VerificationStatusResponseSchema(
            message="Email подтвержден" if user.is_verified else "Email не подтвержден",
            data=status_data,
        )

    def _validate_verification_token(self, token: str) -> int:
        """
        Валидирует токен верификации и возвращает user_id.

        Args:
            token: Токен для проверки

        Returns:
            int: ID пользователя

        Raises:
            TokenInvalidError: Если токен недействителен
            TokenExpiredError: Если токен истек
        """
        try:
            payload = TokenManager.verify_token(token)
            return TokenManager.validate_verification_token(payload)
        except Exception as e:
            self.logger.error("Ошибка валидации токена верификации: %s", e)
            raise

    async def _send_verification_email(self, user: UserModel) -> None:
        """
        Отправляет письмо с токеном верификации пользователю.

        Args:
            user: Модель пользователя, которому отправляется письмо
        """
        try:
            verification_token = TokenManager.generate_verification_token(user.id)
            await self.email_data_manager.send_verification_email(
                to_email=user.email,
                user_name=user.username,
                verification_token=verification_token,
            )
            self.logger.info(
                "Письмо верификации отправлено",
                extra={"user_id": user.id, "email": user.email},
            )
        except Exception as e:
            # Не прерываем регистрацию, если письмо не отправилось
            self.logger.error(
                "Ошибка при отправке письма верификации: %s",
                e,
                extra={"user_id": user.id, "email": user.email},
            )

    async def _send_registration_success_email(self, user_schema) -> None:
        """
        Отправляет письмо об успешной регистрации.

        Args:
            user_schema: Схема пользователя
        """
        try:
            await self.email_data_manager.send_registration_success_email(
                to_email=user_schema.email, user_name=user_schema.username
            )
            self.logger.info(
                "Письмо об успешной регистрации отправлено",
                extra={"user_id": user_schema.id, "email": user_schema.email},
            )
        except Exception as e:
            self.logger.error(
                "Ошибка отправки письма об успешной регистрации: %s",
                e,
                extra={"user_id": user_schema.id, "email": user_schema.email},
            )
