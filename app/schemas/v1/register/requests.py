"""
Схемы для регистрации пользователей.

Модуль содержит Pydantic схемы для валидации данных при регистрации новых пользователей.
Включает валидацию паролей, email адресов и номеров телефонов согласно требованиям безопасности.

Схемы:
    - RegistrationRequestSchema: Схема для входных данных регистрации пользователя
"""

from pydantic import EmailStr, Field, field_validator

from app.core.security.password import BasePasswordValidator
from app.schemas.v1.base import BaseRequestSchema


class RegistrationRequestSchema(BaseRequestSchema):
    """
    Схема для регистрации нового пользователя.

    Наследуется от BaseRequestSchema и предоставляет валидацию всех необходимых
    полей для создания учетной записи пользователя, включая проверку силы пароля
    и корректности формата контактных данных.

    Attributes:
        username (str): Имя пользователя (от 1 до 50 символов)
        email (EmailStr): Email адрес пользователя (автоматическая валидация формата)
        phone (str | None): Номер телефона в российском формате (опционально)
        password (str): Пароль с проверкой требований безопасности

    Validation Rules:
        - username: Обязательное поле, длина от 1 до 50 символов
        - email: Обязательное поле, валидный email формат
        - phone: Опциональное поле, формат +7 (XXX) XXX-XX-XX
        - password: Обязательное поле, проверка через BasePasswordValidator

    Example:
        ```python
        registration_data = RegistrationRequestSchema(
            username="john_doe",
            email="john@example.com",
            phone="+7 (999) 123-45-67",
            password="SecurePass123!"
        )
        ```
    """

    username: str = Field(
        min_length=1,
        max_length=50,
        description="Имя пользователя (от 1 до 50 символов)",
        examples=["john_doe", "user123", "admin"],
    )

    email: EmailStr = Field(
        description="Email адрес пользователя",
        examples=["user@example.com", "john.doe@company.org"],
    )

    phone: str | None = Field(
        default=None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Номер телефона в российском формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67", "+7 (495) 000-00-00"],
    )

    password: str = Field(
        min_length=8,
        description=(
            "Пароль пользователя. Требования: "
            "минимум 8 символов, заглавная и строчная буквы, "
            "цифра, специальный символ"
        ),
        examples=["SecurePass123!", "MyP@ssw0rd"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v, info):
        """
        Валидатор для проверки пароля на соответствие требованиям безопасности.

        Использует BasePasswordValidator для проверки силы пароля, включая:
        - Минимальную длину
        - Наличие заглавных и строчных букв
        - Наличие цифр и специальных символов
        - Отсутствие имени пользователя в пароле

        Args:
            v (str): Пароль для валидации
            info: Контекст валидации с доступом к другим полям

        Returns:
            str: Валидный пароль

        Raises:
            ValueError: Если пароль не соответствует требованиям безопасности

        Note:
            Валидатор автоматически получает username из других полей схемы
            для проверки, что пароль не содержит имя пользователя.
        """
        # Получаем username из контекста для дополнительной проверки
        username = info.data.get("username") if info.data else None

        # Используем базовый валидатор паролей
        return BasePasswordValidator.validate_password_strength(v, username)


class ResendVerificationRequestSchema(BaseRequestSchema):
    """
    Схема запроса на повторную отправку письма верификации

    Attributes:
        email (EmailStr): Email пользователя
    """

    email: EmailStr = Field(description="Email пользователя")
