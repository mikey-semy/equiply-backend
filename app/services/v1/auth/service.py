"""
Модуль для работы с пользователями.
В данном модуле реализованы функции для работы с пользователями.
"""

from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (InvalidCredentialsError, TokenExpiredError,
                                 TokenInvalidError, UserInactiveError)
from app.core.security import PasswordHasher, TokenManager
from app.core.integrations.cache.auth import AuthRedisStorage
from app.schemas import (AuthSchema, TokenResponseSchema,
                         UserCredentialsSchema)
from app.services.v1.base import BaseService
from app.core.settings import settings

from .data_manager import AuthDataManager

class AuthService(BaseService):
    """
    Сервис для аутентификации пользователей.

    Этот класс предоставляет методы для аутентификации пользователей,
    включая создание нового пользователя,
    аутентификацию пользователя и получение токена доступа.

    Args:
        session: Асинхронная сессия для работы с базой данных.

    Methods:
        authenticate: Аутентифицирует пользователя.
        get_token: Получает токен доступа.
    """

    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(session)
        self._data_manager = AuthDataManager(session)
        self._redis_storage = AuthRedisStorage(redis)

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
        user_model = await self._data_manager.get_user_by_identifier(identifier)

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
            raise UserInactiveError(
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
        await self._redis_storage.set_online_status(user_schema.id, True)
        self.logger.info(
            "Пользователь вошел в систему",
            extra={
                "user_id": user_schema.id,
                "email": user_schema.email,
                "is_online": True,
            },
        )

        token = await self.create_token(user_schema)

        await self._redis_storage.update_last_activity(token)

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

        await self._redis_storage.save_token(user_schema, token)
        self.logger.info(
            "Токен сохранен в Redis",
            extra={"user_id": user_schema.id, "token_length": len(token)},
        )

        return TokenResponseSchema(
            access_token=token,
            token_type=settings.TOKEN_TYPE,
        )

    async def logout(self, token: str) -> dict:
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
                await self._redis_storage.set_online_status(user_id, False)
                self.logger.debug(
                    "Пользователь вышел из системы",
                    extra={"user_id": user_id, "is_online": False},
                )
                # Последнюю активность сохраняем в момент выхода
                await self._redis_storage.update_last_activity(token)
            # Удаляем токен из Redis
            await self._redis_storage.remove_token(token)

            return {"message": "Выход выполнен успешно!"}

        except (TokenExpiredError, TokenInvalidError):
            # Даже если токен невалидный, все равно пытаемся его удалить
            await self._redis_storage.remove_token(token)
            return {"message": "Выход выполнен успешно!"}

    async def check_expired_sessions(self):
        """
        Проверяет истекшие сессии и обновляет статус пользователей
        """
        # Получаем все активные токены из Redis
        active_tokens = await self._redis_storage.get_all_tokens()
        now = int(datetime.now(timezone.utc).timestamp())

        for token in active_tokens:
            try:
                payload = TokenManager.decode_token(token)
                # Если токен валидный - пропускаем

                # Получаем время последней активности
                last_activity = await self._redis_storage.get_last_activity(token)

                if now - last_activity > settings.USER_INACTIVE_TIMEOUT:

                    # Неактивен дольше таймаута
                    user_id = payload.get("user_id")
                    user_email = payload.get("sub")

                    if user_id:

                        await self._redis_storage.set_online_status(user_id, False)
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
                    await self._redis_storage.remove_token(token)
            except TokenExpiredError:
                # Токен истек
                user_id = payload.get("user_id")
                user_email = payload.get("sub")

                if user_id:
                    await self._redis_storage.set_online_status(user_id, False)
                    self.logger.debug(
                        "Токен пользователя истек",
                        extra={
                            "user_id": user_id,
                            "email": user_email,
                            "last_activity": last_activity,
                            "now": now,
                        },
                    )
                await self._redis_storage.remove_token(token)

    async def sync_statuses_to_db(self):
        """Синхронизация статусов из Redis в БД"""
        users = await self._data_manager.get_all_users()
        for user in users:
            last_activity = await self._redis_storage.get_last_activity(
                f"token:{user.id}"
            )

            if last_activity:
                last_seen = datetime.fromtimestamp(int(last_activity), tz=timezone.utc)
                await self._data_manager.update_fields(
                    user.id, {"last_seen": last_seen}
                )

    async def get_user_by_identifier(self, identifier: str):
        """
        Получает пользователя по идентификатору (email, username и т.д.)

        Используется в app.core.connections.auth.py

        Args:
            identifier: Идентификатор пользователя

        Returns:
            Модель пользователя или None, если пользователь не найден
        """
        return await self._data_manager.get_user_by_identifier(identifier)
