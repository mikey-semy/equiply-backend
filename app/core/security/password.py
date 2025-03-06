"""
Модуль для работы с паролями.
"""

import logging
import passlib
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=102400,
    argon2__parallelism=8,
)

logger = logging.getLogger(__name__)


class PasswordHasher:
    """
    Класс для хеширования и проверки паролей.
    
    Предоставляет методы для хеширования паролей и проверки хешей.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Генерирует хеш пароля с использованием Argon2.

        Args:
            password: Пароль для хеширования

        Returns:
            Хешированный пароль
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> bool:
        """
        Проверяет, соответствует ли переданный пароль хешу.
        
        Args:
            hashed_password: Хеш пароля.
            plain_password: Пароль для проверки.

        Returns:
            True, если пароль соответствует хешу, иначе False.
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except passlib.exc.UnknownHashError:
            logger.warning("Неизвестный формат хеша пароля")
            return False
