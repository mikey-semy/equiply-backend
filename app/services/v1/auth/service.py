"""
Модуль для работы с пользователями.
В данном модуле реализованы функции для работы с пользователями.
"""

from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (InvalidCredentialsError, TokenExpiredError,
                                 TokenInvalidError, ForbiddenError, UserNotFoundError)
from app.core.security import PasswordHasher, TokenManager
from app.core.integrations.cache.auth import AuthRedisDataManager
from app.schemas import (AuthSchema, TokenResponseSchema, LogoutResponseSchema,
                         UserCredentialsSchema, PasswordResetResponseSchema, PasswordResetConfirmResponseSchema)
from app.services.v1.base import BaseService
from app.core.integrations.mail import AuthEmailDataManager
from app.core.settings import settings

from .data_manager import AuthDataManager

class AuthService(BaseService):
    """
    Сервис для аутентификации пользователей.

    Этот класс предоставляет методы для аутентификации пользователей,
    включая выход пользователя из системы, восстановление пароля.

    Attributes:
        session: Асинхронная сессия для работы с базой данных.
        redis: Redis ...

    Methods:
        authenticate: Аутентифицирует пользователя.
        create_token: Создание JWT токена
        logout: Выполняет выход пользователя, удаляя токен из Redis.
        check_expired_sessions: Проверяет истекшие сессии и обновляет статус пользователей
        get_user_by_identifier: Получает пользователя по идентификатору (email, username и т.д.)
        send_password_reset_email: Отправляет email со ссылкой для сброса пароля
        reset_password: Устанавливает новый пароль по токену сброса
        _generate_password_reset_token: Генерирует токен для сброса пароля
    """

    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(session)
        self.data_manager = AuthDataManager(session)
        self.redis_data_manager = AuthRedisDataManager(redis)
        self.email_data_manager = AuthEmailDataManager()

    async def authenticate(self, form_data: OAuth2PasswordRequestForm) -> TokenResponseSchema:
        """
        Аутентифицирует пользователя по логину и паролю.

        Args:
            form_data: Данные для аутентификации пользователя.

        Returns:
            TokenResponseSchema: Токен доступа.

        Raises:
            InvalidCredentialsError: Если пользователь не найден или пароль неверный.
        """
        credentials = AuthSchema(username=form_data.username, password=form_data.password)

        identifier = credentials.username

        self.logger.info(
            "Попытка аутентификации",
            extra={
                "identifier": identifier,
                "has_password": bool(credentials.password),
            },
        )

        # Пытаемся найти пользователя по email, телефону или имени пользователя
        user_model = await self.data_manager.get_user_by_identifier(identifier)

        self.logger.info(
            "Начало аутентификации",
            extra={"identifier": identifier, "user_found": bool(user_model)},
        )

        if not user_model:
            self.logger.warning("Пользователь не найден", extra={"identifier": identifier})
            raise InvalidCredentialsError()

        if not user_model.is_active:
            self.logger.warning(
                "Попытка входа в неактивный аккаунт",
                extra={"identifier": identifier, "user_id": user_model.id},
            )
            raise ForbiddenError(
                detail="Аккаунт деактивирован", extra={"identifier": credentials.username}
            )

        if not user_model or not PasswordHasher.verify(
            user_model.hashed_password, credentials.password
        ):
            self.logger.warning(
                "Неверный пароль",
                extra={"identifier": identifier, "user_id": user_model.id},
            )
            raise InvalidCredentialsError()

        user_schema = UserCredentialsSchema.model_validate(user_model)

        if not user_schema.is_verified:
            self.logger.warning(
                "Вход с неподтвержденным аккаунтом",
                extra={"identifier": identifier, "user_id": user_model.id},
            )

        self.logger.info(
            "Аутентификация успешна",
            extra={
                "user_id": user_schema.id,
                "email": user_schema.email,
                "role": user_schema.role
            },
        )
        await self.redis_data_manager.set_online_status(user_schema.id, True)
        self.logger.info(
            "Пользователь вошел в систему",
            extra={
                "user_id": user_schema.id,
                "email": user_schema.email,
                "is_online": True,
            },
        )

        token = await self.create_token(user_schema)

        await self.redis_data_manager.update_last_activity(token)

        return token

    async def create_token(
        self, user_schema: UserCredentialsSchema
    ) -> TokenResponseSchema:
        """
        Создание JWT токена

        Args:
            user_schema: Данные пользователя

        Returns:
            TokenResponseSchema: Схема с access_token и token_type
        """
        payload = TokenManager.create_payload(user_schema)
        self.logger.debug("Создан payload токена", extra={"payload": payload})

        token = TokenManager.generate_token(payload)
        self.logger.debug("Сгенерирован токен", extra={"token_length": len(token)})

        await self.redis_data_manager.save_token(user_schema, token)
        self.logger.info(
            "Токен сохранен в Redis",
            extra={"user_id": user_schema.id, "token_length": len(token)},
        )

        return TokenResponseSchema(access_token=token)

    async def logout(self, token: str) -> LogoutResponseSchema:
        """
        Выполняет выход пользователя, удаляя токен из Redis.
        Отправляем сообщение об успешном завершении.

        Args:
            token: Токен для выхода.

        Returns:
            Сообщение об успешном завершении.
        """

        try:
            # Получаем данные из токена
            payload = TokenManager.decode_token(token)

            # Получаем user_id пользователя
            user_id = payload.get("user_id")

            if user_id:
                await self.redis_data_manager.set_online_status(user_id, False)
                self.logger.debug(
                    "Пользователь вышел из системы",
                    extra={"user_id": user_id, "is_online": False},
                )
                # Последнюю активность сохраняем в момент выхода
                await self.redis_data_manager.update_last_activity(token)
            # Удаляем токен из Redis
            await self.redis_data_manager.remove_token(token)

            return LogoutResponseSchema()

        except (TokenExpiredError, TokenInvalidError):
            # Даже если токен невалидный, все равно пытаемся его удалить
            await self.redis_data_manager.remove_token(token)
            return LogoutResponseSchema()

    async def check_expired_sessions(self):
        """
        Проверяет истекшие сессии и обновляет статус пользователей
        """
        # Получаем все активные токены из Redis
        active_tokens = await self.redis_data_manager.get_all_tokens()
        now = int(datetime.now(timezone.utc).timestamp())

        for token in active_tokens:
            try:
                payload = TokenManager.decode_token(token)
                # Если токен валидный - пропускаем

                # Получаем время последней активности
                last_activity = await self.redis_data_manager.get_last_activity(token)

                if now - last_activity > settings.USER_INACTIVE_TIMEOUT:

                    # Неактивен дольше таймаута
                    user_id = payload.get("user_id")
                    user_email = payload.get("sub")

                    if user_id:

                        await self.redis_data_manager.set_online_status(user_id, False)
                        self.logger.debug(
                            "Пользователь не активен дольше таймаута",
                            extra={
                                "user_id": user_id,
                                "email": user_email,
                                "last_activity": last_activity,
                                "now": now,
                                "timeout": settings.USER_INACTIVE_TIMEOUT,
                            },
                        )
                    await self.redis_data_manager.remove_token(token)
            except TokenExpiredError:
                # Токен истек
                user_id = payload.get("user_id")
                user_email = payload.get("sub")

                if user_id:
                    await self.redis_data_manager.set_online_status(user_id, False)
                    self.logger.debug(
                        "Токен пользователя истек",
                        extra={
                            "user_id": user_id,
                            "email": user_email,
                            "last_activity": last_activity,
                            "now": now,
                        },
                    )
                await self.redis_data_manager.remove_token(token)

    async def get_user_by_identifier(self, identifier: str):
        """
        Получает пользователя по идентификатору (email, username и т.д.)

        Используется в app.core.connections.auth.py

        Args:
            identifier: Идентификатор пользователя

        Returns:
            Модель пользователя или None, если пользователь не найден
        """
        return await self.data_manager.get_user_by_identifier(identifier)

    async def send_password_reset_email(self, email: str) -> PasswordResetResponseSchema:
        """
        Отправляет email со ссылкой для сброса пароля

        Args:
            email: Email пользователя

        Returns:
            PasswordResetResponseSchema: Сообщение об успехе

        Raises:
            UserNotFoundError: Если пользователь с указанным email не найден
        """
        self.logger.info("Запрос на сброс пароля", extra={"email": email})

        # Проверяем существование пользователя
        user = await self.data_manager.get_user_by_identifier(email)
        if not user:
            self.logger.warning("Пользователь не найден", extra={"email": email})
            # Не сообщаем об отсутствии пользователя в ответе из соображений безопасности
            return PasswordResetResponseSchema(
                success=True,
                message="Инструкции по сбросу пароля отправлены на ваш email"
            )

        # Генерируем токен для сброса пароля
        reset_token = self._generate_password_reset_token(user.id)

        try:
            await self.email_data_manager.send_password_reset_email(
                to_email=user.email,
                user_name=user.username,
                reset_token=reset_token
            )

            self.logger.info(
                "Письмо для сброса пароля отправлено",
                extra={"user_id": user.id, "email": user.email}
            )

            return PasswordResetResponseSchema(
                success=True,
                message="Инструкции по сбросу пароля отправлены на ваш email"
            )

        except Exception as e:
            self.logger.error("Ошибка при отправке письма сброса пароля: %s", e, extra={"email": email})
            raise

    async def reset_password(self, token: str, new_password: str) -> PasswordResetConfirmResponseSchema:
        """
        Устанавливает новый пароль по токену сброса

        Args:
            token: Токен сброса пароля
            new_password: Новый пароль

        Returns:
            PasswordResetConfirmResponseSchema: Сообщение об успехе

        Raises:
            TokenInvalidError: Если токен недействителен
            TokenExpiredError: Если токен истек
            UserNotFoundError: Если пользователь не найден
        """
        self.logger.info("Запрос на установку нового пароля")

        try:
            # Проверяем и декодируем токен
            payload = TokenManager.verify_token(token)

            # Проверяем тип токена
            if payload.get('type') != 'password_reset':
                self.logger.warning("Неверный тип токена", extra={"type": payload.get('type')})
                raise TokenInvalidError()

            # Получаем ID пользователя
            user_id = int(payload['sub'])

            # Проверяем существование пользователя
            user = await self.data_manager.get_item_by_field("id", user_id)
            if not user:
                self.logger.warning("Пользователь не найден", extra={"user_id": user_id})
                raise UserNotFoundError(field="id", value=user_id)

            # Хешируем новый пароль
            hashed_password = PasswordHasher.hash_password(new_password)

            # Обновляем пароль в БД
            await self.data_manager.update_items(
                user_id,
                {"hashed_password": hashed_password}
            )

            self.logger.info("Пароль успешно изменен", extra={"user_id": user_id})
            return PasswordResetConfirmResponseSchema(
                success=True,
                message="Пароль успешно изменен"
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.error("Ошибка проверки токена сброса пароля: %s", e)
            raise
        except Exception as e:
            self.logger.error("Ошибка при сбросе пароля: %s", e)
            raise

    def _generate_password_reset_token(self, user_id: int) -> str:
        """
        Генерирует токен для сброса пароля

        Args:
            user_id: ID пользователя

        Returns:
            str: Токен для сброса пароля
        """
        payload = {
            'sub': str(user_id),
            'type': 'password_reset',
            'expires_at': (
                int(datetime.now(timezone.utc).timestamp()) +
                1800  # 30 минут (в секундах)
            )
        }
        return TokenManager.generate_token(payload)
