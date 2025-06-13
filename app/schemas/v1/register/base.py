"""
Схемы данных для регистрации пользователей.

Содержит классы данных, которые помещаются в поле `data` ответов API.
Эти схемы описывают структуру полезной нагрузки ответов регистрации.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.v1.base import BaseCommonResponseSchema


class RegistrationDataSchema(BaseCommonResponseSchema):
    """
    Схема данных пользователя при успешной регистрации.

    Содержит основную информацию о зарегистрированном пользователе,
    которая безопасна для передачи клиенту. Исключает конфиденциальные
    данные такие как хешированный пароль.

    Attributes:
        id: Уникальный UUID идентификатор пользователя в системе
        username: Имя пользователя для входа в систему
        email: Email адрес пользователя
        role: Роль пользователя в системе (по умолчанию "user")
        is_active: Статус активности аккаунта
        is_verified: Статус верификации email (False при регистрации)
        created_at: Дата и время создания аккаунта
        access_token: Ограниченный JWT токен доступа (до верификации)
        refresh_token: JWT токен для обновления access токена
        token_type: Тип токена (всегда "bearer")
        requires_verification: Флаг необходимости верификации email

    Example:
        ```python
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "john_doe",
            "email": "john@example.com",
            "role": "user",
            "is_active": true,
            "is_verified": false,
            "created_at": "2024-01-15T10:30:00Z",
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "requires_verification": true
        }
        ```
    """

    id: uuid.UUID = Field(
        description="Уникальный UUID идентификатор пользователя",
        examples=[
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
        ],
    )

    username: str = Field(
        description="Имя пользователя для входа в систему",
        examples=["john_doe", "user123", "admin"],
    )

    email: EmailStr = Field(
        description="Email адрес пользователя",
        examples=["user@example.com", "john.doe@company.org"],
    )

    role: str = Field(
        default="user",
        description="Роль пользователя в системе",
        examples=["user", "admin", "moderator"],
    )

    is_active: bool = Field(
        default=True, description="Статус активности аккаунта пользователя"
    )

    is_verified: bool = Field(
        default=False, description="Статус верификации email или телефона"
    )

    created_at: datetime = Field(
        description="Дата и время создания аккаунта", examples=["2024-01-15T10:30:00Z"]
    )

    access_token: Optional[str] = Field(
        default=None,
        description="Ограниченный JWT токен доступа (до верификации email). "
        "Будет None если используются cookies (use_cookies=true)",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", None],
    )

    refresh_token: Optional[str] = Field(
        default=None,
        description="JWT токен для обновления access токена. "
        "Будет None если используются cookies (use_cookies=true)",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", None],
    )

    token_type: str = Field(default="bearer", description="Тип токена (всегда bearer)")

    requires_verification: bool = Field(
        default=True, description="Требуется ли верификация email для полного доступа"
    )


class VerificationDataSchema(BaseCommonResponseSchema):
    """
    Данные верификации email адреса.

    Содержит информацию о результате подтверждения email
    и новые полные токены доступа после верификации.

    Attributes:
        id: UUID верифицированного пользователя
        email: Верифицированный email адрес
        verified_at: Время подтверждения email в UTC
        access_token: Новый полный JWT токен доступа (без ограничений)
        refresh_token: Новый JWT токен для обновления
        token_type: Тип токена (всегда "bearer")

    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "john@example.com",
            "verified_at": "2024-01-15T10:35:00Z",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        ```
    """

    id: uuid.UUID = Field(
        description="UUID верифицированного пользователя",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    email: EmailStr = Field(
        description="Верифицированный email адрес", example="john@example.com"
    )
    verified_at: datetime = Field(
        description="Время подтверждения email в формате UTC",
        example="2024-01-15T10:35:00Z",
    )
    access_token: Optional[str] = Field(
        default=None,
        description="Новый полный JWT токен доступа (без ограничений). "
        "Будет None если используются cookies (use_cookies=true)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", None],
    )
    refresh_token: Optional[str] = Field(
        default=None,
        description="Новый JWT токен для обновления access токена. "
        "Будет None если используются cookies (use_cookies=true)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", None],
    )
    token_type: str = Field(default="bearer", description="Тип токена (всегда bearer)")


class ResendVerificationDataSchema(BaseCommonResponseSchema):
    """
    Данные повторной отправки письма верификации.

    Содержит информацию о повторной отправке письма подтверждения.
    Возвращается при запросе на повторную отправку токена верификации.

    Attributes:
        email: Email адрес, на который отправлено письмо
        sent_at: Время отправки письма
        expires_in: Время действия токена в секундах
    """

    email: EmailStr = Field(
        description="Email адрес для повторной отправки", example="john@example.com"
    )
    sent_at: datetime = Field(
        description="Время отправки письма в формате UTC",
        example="2024-01-15T10:40:00Z",
    )
    expires_in: int = Field(
        description="Время действия токена верификации в секундах", example=3600
    )


class VerificationStatusDataSchema(BaseCommonResponseSchema):
    """
    Данные статуса верификации email.

    Содержит информацию о текущем статусе верификации
    email адреса пользователя.

    Attributes:
        email: Проверяемый email адрес
        is_verified: Статус верификации (true/false)
        checked_at: Время проверки статуса в UTC

    Example:
        ```json
        {
            "email": "john@example.com",
            "is_verified": true,
            "checked_at": "2024-01-15T10:45:00Z"
        }
        ```
    """

    email: EmailStr = Field(
        description="Проверяемый email адрес", example="john@example.com"
    )
    is_verified: bool = Field(description="Статус верификации email", example=True)
    checked_at: datetime = Field(
        description="Время проверки статуса в UTC", example="2024-01-15T10:45:00Z"
    )
