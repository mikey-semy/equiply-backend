"""
Схемы данных для аутентификации.

Содержит классы данных, которые помещаются в поле `data` ответов API.
Эти схемы описывают структуру полезной нагрузки ответов.
"""

from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.v1.base import BaseCommonResponseSchema


class TokenDataSchema(BaseCommonResponseSchema):
    """
    ! не используется из-за Swagger UI

    Данные токенов аутентификации.

    Содержит информацию о выданных токенах доступа и их параметрах.
    Используется в ответах на запросы аутентификации и обновления токенов.

    Attributes:
        access_token: JWT токен для доступа к защищенным ресурсам
        refresh_token: Токен для обновления access_token без повторной аутентификации
        token_type: Тип токена (всегда Bearer для JWT)
        expires_in: Время жизни access_token в секундах
    """

    access_token: str = Field(
        description="JWT токен доступа для авторизации запросов",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    refresh_token: str = Field(
        description="Токен для обновления access_token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    token_type: str = Field(
        default="Bearer", description="Тип токена для заголовка Authorization"
    )
    expires_in: int = Field(
        description="Время жизни access_token в секундах", example=1800
    )


class LogoutDataSchema(BaseCommonResponseSchema):
    """
    Данные выхода из системы.

    Содержит информацию о времени выполнения операции выхода.
    Подтверждает успешное завершение сессии пользователя.

    Attributes:
        logged_out_at: Временная метка выхода из системы в UTC
    """

    logged_out_at: datetime = Field(
        description="Время выхода из системы в формате UTC",
        example="2024-01-15T10:30:00Z",
    )


class PasswordResetDataSchema(BaseCommonResponseSchema):
    """
    Данные запроса сброса пароля.

    Содержит информацию о запросе на восстановление пароля.
    Подтверждает отправку письма с инструкциями.

    Attributes:
        email: Email адрес, на который отправлены инструкции
        expires_in: Время действия ссылки восстановления в секундах
    """

    email: EmailStr = Field(
        description="Email адрес для восстановления пароля", example="user@example.com"
    )
    expires_in: int = Field(
        description="Время действия ссылки восстановления в секундах", example=1800
    )


class PasswordResetConfirmDataSchema(BaseCommonResponseSchema):
    """
    Данные подтверждения сброса пароля.

    Содержит информацию об успешном изменении пароля.
    Подтверждает завершение процедуры восстановления.

    Attributes:
        password_changed_at: Временная метка изменения пароля в UTC
    """

    password_changed_at: datetime = Field(
        description="Время изменения пароля в формате UTC",
        example="2024-01-15T10:35:00Z",
    )
