"""
Модуль для работы с пользователями.
В данном модуле реализованы функции для работы с пользователями.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import Response
from fastapi.security import OAuth2PasswordRequestForm
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (ForbiddenError, InvalidCredentialsError,
                                 TokenExpiredError, TokenInvalidError,
                                 UserNotFoundError)
from app.core.integrations.cache.auth import AuthRedisDataManager
from app.core.integrations.mail import AuthEmailDataManager
from app.core.security import PasswordHasher, TokenManager, CookieManager
from app.core.settings import settings
from app.schemas import (AuthSchema, LogoutDataSchema,
                         LogoutResponseSchema, PasswordResetConfirmDataSchema,
                         PasswordResetConfirmResponseSchema,
                         PasswordResetConfirmSchema, PasswordResetDataSchema,
                         PasswordResetResponseSchema, TokenResponseSchema,
                         UserCredentialsSchema)
from app.services.v1.base import BaseService

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
        authenticate: Аутентифицирует пользователя
        create_token: Создание JWT токена
        create_refresh_token: Создание JWT refresh токена
        refresh_token: Обновляет access токен с помощью refresh токена
        logout: Выполняет выход пользователя, удаляя токен из Redis
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

    async def authenticate(
        self,
        form_data: OAuth2PasswordRequestForm,
        response: Optional[Response] = None,
        use_cookies: bool = False,

    ) -> TokenResponseSchema:
        """
        Аутентифицирует пользователя по логину и паролю.

        Args:
            form_data: Данные для аутентификации пользователя.

        Returns:
            TokenResponseSchema: Токен доступа.

        Raises:
            InvalidCredentialsError: Если пользователь не найден или пароль неверный.
        """
        credentials = AuthSchema(
            username=form_data.username, password=form_data.password
        )

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
            self.logger.warning(
                "Пользователь не найден", extra={"identifier": identifier}
            )
            raise InvalidCredentialsError()

        if not user_model.is_active:
            self.logger.warning(
                "Попытка входа в неактивный аккаунт",
                extra={"identifier": identifier, "user_id": user_model.id},
            )
            raise ForbiddenError(
                detail="Аккаунт деактивирован",
                extra={"identifier": credentials.username},
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
                "role": user_schema.role,
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

        access_token = await self.create_token(user_schema)
        refresh_token = await self.create_refresh_token(user_schema.id)

        await self.redis_data_manager.update_last_activity(access_token)

        # Опционально устанавливаем куки
        if response and use_cookies:
            CookieManager.set_auth_cookies(response, access_token, refresh_token)

            return TokenResponseSchema(
                message="Аутентификация успешна",
                access_token=None,
                refresh_token=None,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        return TokenResponseSchema(
            message="Аутентификация успешна",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

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

        access_token = TokenManager.generate_token(payload)
        self.logger.debug("Сгенерирован токен", extra={"access_token_length": len(access_token)})

        await self.redis_data_manager.save_token(user_schema, access_token)
        self.logger.info(
            "Токен сохранен в Redis",
            extra={"user_id": user_schema.id, "access_token_length": len(access_token)},
        )

        return access_token

    async def create_refresh_token(self, user_id: uuid.UUID) -> str:
        """
        Создание JWT refresh токена

        Args:
            user_id: ID пользователя

        Returns:
            str: Refresh токен
        """
        payload = TokenManager.create_refresh_payload(user_id)
        self.logger.debug("Создан payload refresh токена", extra={"payload": payload})

        refresh_token = TokenManager.generate_token(payload)
        self.logger.debug("Сгенерирован refresh токен", extra={"refresh_token_length": len(refresh_token)})

        # Сохраняем refresh токен в Redis
        await self.redis_data_manager.save_refresh_token(user_id, refresh_token)
        self.logger.info(
            "Refresh токен сохранен в Redis",
            extra={"user_id": user_id, "refresh_token_length": len(refresh_token)},
        )

        return refresh_token

    async def refresh_token(
        self,
        refresh_token: str,
        response: Optional[Response] = None,
        use_cookies: bool = False
    ) -> TokenResponseSchema:
        """
        Обновляет access токен с помощью refresh токена.

        Args:
            refresh_token: Refresh токен.

        Returns:
            TokenResponseSchema: Новые токены доступа.

        Raises:
            TokenInvalidError: Если refresh токен недействителен.
            TokenExpiredError: Если refresh токен истек.
        """
        try:
            # Декодируем refresh токен
            payload = TokenManager.decode_token(refresh_token)

            # Валидируем refresh токен
            user_id = TokenManager.validate_refresh_token(payload)

            # Проверяем, что refresh токен существует в Redis
            if not await self.redis_data_manager.check_refresh_token(user_id, refresh_token):
                self.logger.warning(
                    "Попытка использовать неизвестный refresh токен",
                    extra={"user_id": user_id},
                )
                raise TokenInvalidError()

            # Получаем пользователя
            user_model = await self.data_manager.get_item_by_field("id", user_id)

            if not user_model:
                self.logger.warning(
                    "Пользователь не найден при обновлении токена",
                    extra={"user_id": user_id},
                )
                raise UserNotFoundError(field="id", value=user_id)

            user_schema = UserCredentialsSchema.model_validate(user_model)

            # Создаем новые токены
            access_token = await self.create_token(user_schema)
            new_refresh_token = await self.create_refresh_token(user_id)

            # Удаляем старый refresh токен
            await self.redis_data_manager.remove_refresh_token(user_id, refresh_token)

            self.logger.info(
                "Токены успешно обновлены",
                extra={"user_id": user_id},
            )

            # Опционально обновляем куки
            if response and use_cookies:
                CookieManager.set_auth_cookies(
                    response, access_token, new_refresh_token
                )

                return TokenResponseSchema(
                    message="Токен успешно обновлен",
                    access_token=None,
                    refresh_token=None,
                    expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                )

            return TokenResponseSchema(
                message="Токен успешно обновлен",
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.warning(
                "Ошибка при обновлении токена: %s",
                type(e).__name__,
                extra={"error_type": type(e).__name__}
            )
            raise

    async def logout(
        self,
        authorization: Optional[str],
        response: Optional[Response] = None,
        clear_cookies: bool = False,
    ) -> LogoutResponseSchema:
        """
        Выполняет выход пользователя, удаляя токен из Redis.
        Отправляем сообщение об успешном завершении.

        Args:
            authorization: Заголовок Authorization с токеном Bearer

        Returns:
            LogoutResponseSchema: Сообщение об успешном завершении.

        Raises:
            TokenMissingError: Если заголовок Authorization отсутствует
            TokenInvalidError: Если формат заголовка неверный
            TokenExpiredError: Если токен просрочен
        """
        try:
            # Извлекаем токен из заголовка
            token = TokenManager.get_token_from_header(authorization)

            try:
                # Получаем данные из токена
                payload = TokenManager.decode_token(token)

                # Получаем user_id пользователя
                user_id = payload.get("user_id")

                if user_id:
                    await self.redis_data_manager.set_online_status(user_id, False)

                    # Удаляем все refresh токены пользователя
                    await self.redis_data_manager.remove_all_refresh_tokens(user_id)

                    self.logger.debug(
                        "Пользователь вышел из системы, все токены удалены",
                        extra={"user_id": user_id, "is_online": False},
                    )

                    # Последнюю активность сохраняем в момент выхода
                    await self.redis_data_manager.update_last_activity(token)

            except (TokenExpiredError, TokenInvalidError) as e:
                # Логируем проблему с токеном, но продолжаем процесс выхода
                self.logger.warning(
                    "Выход с невалидным токеном: %s",
                    type(e).__name__,
                    extra={"token_error": type(e).__name__},
                )

            # Удаляем токен из Redis
            await self.redis_data_manager.remove_token(token)
            logout_data = LogoutDataSchema(logged_out_at=datetime.now(timezone.utc))

            # Опционально очищаем куки
            if response and clear_cookies:
                CookieManager.clear_auth_cookies(response)

            return LogoutResponseSchema(
                message="Выход выполнен успешно", data=logout_data
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            # Для этих ошибок мы не можем продолжить процесс выхода
            self.logger.warning(
                "Ошибка при выходе: %s",
                type(e).__name__,
                extra={"error_type": type(e).__name__},
            )
            # Пробрасываем исключение дальше для обработки на уровне API
            raise

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

    async def send_password_reset_email(
        self, email: str
    ) -> PasswordResetResponseSchema:
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
                message="Инструкции по сбросу пароля отправлены на ваш email",
            )

        # Генерируем токен для сброса пароля
        reset_token = self._generate_password_reset_token(user.id)

        try:
            await self.email_data_manager.send_password_reset_email(
                to_email=user.email, user_name=user.username, reset_token=reset_token
            )

            self.logger.info(
                "Письмо для сброса пароля отправлено",
                extra={"user_id": user.id, "email": user.email},
            )

            return PasswordResetResponseSchema(
                success=True,
                message="Инструкции по сбросу пароля отправлены на ваш email",
            )

        except Exception as e:
            self.logger.error(
                "Ошибка при отправке письма сброса пароля: %s",
                e,
                extra={"email": email},
            )
            raise

    async def reset_password(
        self, token: str, new_password: str
    ) -> PasswordResetConfirmResponseSchema:
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
            if payload.get("type") != "password_reset":
                self.logger.warning(
                    "Неверный тип токена", extra={"type": payload.get("type")}
                )
                raise TokenInvalidError()

            # Получаем ID пользователя
            user_id = int(payload["sub"])

            # Проверяем существование пользователя
            user = await self.data_manager.get_item_by_field("id", user_id)
            if not user:
                self.logger.warning(
                    "Пользователь не найден", extra={"user_id": user_id}
                )
                raise UserNotFoundError(field="id", value=user_id)

            # Хешируем новый пароль
            hashed_password = PasswordHasher.hash_password(new_password)

            # Обновляем пароль в БД
            await self.data_manager.update_items(
                user_id, {"hashed_password": hashed_password}
            )

            self.logger.info("Пароль успешно изменен", extra={"user_id": user_id})
            return PasswordResetConfirmResponseSchema(
                success=True, message="Пароль успешно изменен"
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.error("Ошибка проверки токена сброса пароля: %s", e)
            raise
        except Exception as e:
            self.logger.error("Ошибка при сбросе пароля: %s", e)
            raise

    def _generate_password_reset_token(self, user_id: uuid.UUID) -> str:
        """
        Генерирует токен для сброса пароля

        Args:
            user_id: ID пользователя

        Returns:
            str: Токен для сброса пароля
        """
        payload = {
            "sub": str(user_id),
            "type": "password_reset",
            "expires_at": (
                int(datetime.now(timezone.utc).timestamp())
                + 1800  # 30 минут (в секундах)
            ),
        }
        return TokenManager.generate_token(payload)
