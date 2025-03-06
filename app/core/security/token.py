"""
Модуль для работы с токенами.
"""

import logging
from datetime import datetime, timezone

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from app.core.exceptions import (InvalidCredentialsError, TokenExpiredError,
                               TokenInvalidError, TokenMissingError)
from app.schemas import UserCredentialsSchema

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Класс для работы с JWT токенами.
    
    Предоставляет методы для генерации, проверки и валидации токенов.
    """

    @staticmethod
    def generate_token(payload: dict) -> str:
        """
        Генерирует JWT токен.

        Args:
            payload: Данные для токена

        Returns:
            JWT токен
        """
        from app.core.settings import settings

        return jwt.encode(
            payload, key=TokenManager.get_token_key(), algorithm=settings.TOKEN_ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Декодирует JWT токен.

        Args:
            token: JWT токен

        Returns:
            Декодированные данные

        Raises:
            TokenExpiredError: Если токен просрочен
            TokenInvalidError: Если токен невалиден
        """
        from app.core.settings import settings

        try:
            return jwt.decode(
                token,
                key=TokenManager.get_token_key(),
                algorithms=[settings.TOKEN_ALGORITHM],
            )
        except ExpiredSignatureError as error:
            raise TokenExpiredError() from error
        except JWTError as error:
            raise TokenInvalidError() from error

    @staticmethod
    def create_payload(user: UserCredentialsSchema) -> dict:
        """
        Создает payload для токена.

        Args:
            user: Данные пользователя

        Returns:
            Payload для JWT
        """
        expires_at = (
            int(datetime.now(timezone.utc).timestamp())
            + TokenManager.get_token_expiration()
        )
        return {"sub": user.email, "expires_at": expires_at}

    @staticmethod
    def get_token_key() -> str:
        """
        Получает секретный ключ для токена.

        Returns:
            Секретный ключ для токена.
        """
        from app.core.settings import settings

        return settings.TOKEN_SECRET_KEY.get_secret_value()

    @staticmethod
    def get_token_expiration() -> int:
        """
        Получает время истечения срока действия токена в секундах.

        Example:
            1440 минут * 60 = 86400 секунд (24 часа)

        Returns:
            Количество секунд до истечения токена
        """
        from app.core.settings import settings

        return settings.TOKEN_EXPIRE_MINUTES * 60

    @staticmethod
    def is_expired(expires_at: int) -> bool:
        """
        Проверяет, истек ли срок действия токена.

        Args:
            expires_at: Время истечения в секундах

        Returns:
            True, если токен истек, иначе False.
        """
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        return current_timestamp > expires_at

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Проверяет JWT токен и возвращает payload.

        Args:
            token: Токен пользователя.

        Returns:
            payload: Данные пользователя.
            
        Raises:
            TokenMissingError: Если токен отсутствует
        """
        if not token:
            raise TokenMissingError()
        return TokenManager.decode_token(token)

    @staticmethod
    def validate_payload(payload: dict) -> str:
        """
        Валидирует данные из payload.

        Args:
            payload: Данные пользователя.

        Returns:
            email: Email пользователя.
            
        Raises:
            InvalidCredentialsError: Если email отсутствует
            TokenExpiredError: Если токен просрочен
        """
        email = payload.get("sub")
        expires_at = payload.get("expires_at")

        if not email:
            raise InvalidCredentialsError()

        if TokenManager.is_expired(expires_at):
            raise TokenExpiredError()

        return email
