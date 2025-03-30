"""
Модуль для работы с паролями.

- BasePasswordValidator предоставляет статический метод validate_password_strength, который может быть вызван из любой схемы для проверки пароля.

- RegistrationSchema определяет валидатор поля password, который вызывает BasePasswordValidator.validate_password_strength и передаёт как пароль, так и имя пользователя для дополнительной проверки.

- PasswordFormSchema определяет валидатор поля new_password, который вызывает тот же метод BasePasswordValidator.validate_password_strength.

Процесс валидации:

- Когда данные отправляются в любую из этих схем
- Pydantic запускает валидацию всех полей
- Для полей password (в RegistrationSchema) и new_password (в PasswordFormSchema) вызываются наши валидаторы
- Валидаторы вызывают статический метод validate_password_strength
- Этот метод проверяет пароль на соответствие всем требованиям
- Если пароль не соответствует требованиям, выбрасывается исключение WeakPasswordError
- Это исключение содержит детальное описание всех проблем с паролем
"""

import logging
import re

import passlib
from passlib.context import CryptContext
from pydantic import BaseModel, field_validator

from app.core.exceptions.auth import WeakPasswordError

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


class BasePasswordValidator(BaseModel):
    """
    Базовый класс для валидации паролей по стандартам безопасности.

    Требования к паролю:
    - Минимум 8 символов
    - Минимум 1 заглавная буква
    - Минимум 1 строчная буква
    - Минимум 1 цифра
    - Минимум 1 специальный символ
    - Не содержит username, если он указан
    """

    @staticmethod
    def validate_password_strength(password: str, username: str = None) -> str:
        """
        Проверяет сложность пароля на соответствие требованиям безопасности.

        Args:
            password: Пароль для проверки
            username: Имя пользователя для проверки, что пароль его не содержит

        Returns:
            Проверенный пароль, если он соответствует требованиям

        Raises:
            WeakPasswordError: Если пароль не соответствует требованиям безопасности
        """
        errors = []

        # Проверка минимальной длины
        if len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов")

        # Проверка на наличие заглавной буквы
        if not re.search(r"[A-ZА-Я]", password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву")

        # Проверка на наличие строчной буквы
        if not re.search(r"[a-zа-я]", password):
            errors.append("Пароль должен содержать хотя бы одну строчную букву")

        # Проверка на наличие цифры
        if not re.search(r"\d", password):
            errors.append("Пароль должен содержать хотя бы одну цифру")

        # Проверка на наличие специального символа
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Пароль должен содержать хотя бы один специальный символ")

        # Проверка распространенных последовательностей
        common_sequences = [
            "12345",
            "qwerty",
            "password",
            "admin",
            "123456789",
            "abc123",
        ]
        if any(seq in password.lower() for seq in common_sequences):
            errors.append(
                "Пароль не должен содержать распространенные последовательности"
            )

        # Проверка, что пароль не содержит имя пользователя
        if username and len(username) > 3:
            if username.lower() in password.lower():
                errors.append("Пароль не должен содержать имя пользователя")

        if errors:
            # Вызываем существующее исключение с детальным сообщением об ошибках
            raise WeakPasswordError("; ".join(errors))

        return password
