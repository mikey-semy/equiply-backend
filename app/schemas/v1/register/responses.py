"""
Схемы ответов для регистрации пользователей.

Содержит Pydantic схемы для исходящих данных endpoints регистрации.
Все схемы следуют единому формату: {success, message, data}.
"""

from app.schemas.v1.base import BaseResponseSchema

from .base import (RegistrationDataSchema, ResendVerificationDataSchema,
                   VerificationDataSchema, VerificationStatusDataSchema)


class RegistrationResponseSchema(BaseResponseSchema):
    """
    Схема полного ответа API при успешной регистрации пользователя.

    Содержит стандартные поля ответа (success, message) плюс данные
    зарегистрированного пользователя с ограниченными токенами.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Информационное сообщение о результате регистрации
        data: Данные зарегистрированного пользователя с токенами

    Example:
        ```json
        {
            "success": true,
            "message": "Регистрация завершена. Подтвердите email для полного доступа.",
            "data": {
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
        }
        ```
    """

    data: RegistrationDataSchema


class VerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа при успешной верификации email.

    Возвращается после подтверждения email адреса по токену из письма.
    Содержит новые полные токены доступа без ограничений.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Сообщение о результате верификации
        data: Данные о верификации с новыми токенами

    Example:
        ```json
        {
            "success": true,
            "message": "Email успешно подтвержден. Теперь вы можете войти в систему",
            "data": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john@example.com",
                "verified_at": "2024-01-15T10:35:00Z",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
        ```
    """

    data: VerificationDataSchema


class ResendVerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа при повторной отправке письма верификации.

    Возвращается при запросе на повторную отправку токена подтверждения email.
    Содержит информацию о новом письме и времени его действия.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Сообщение о результате отправки
        data: Данные о повторной отправке

    Example:
        ```json
        {
            "success": true,
            "message": "Письмо верификации отправлено повторно",
            "data": {
                "email": "john@example.com",
                "sent_at": "2024-01-15T10:40:00Z",
                "expires_in": 3600
            }
        }
        ```
    """

    data: ResendVerificationDataSchema


class VerificationStatusResponseSchema(BaseResponseSchema):
    """
    Схема ответа о статусе верификации email.

    Возвращает текущий статус верификации email адреса пользователя.
    Используется для проверки необходимости повторной отправки письма.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Сообщение о статусе верификации
        data: Данные о статусе верификации

    Example:
        ```json
        {
            "success": true,
            "message": "Email подтвержден",
            "data": {
                "email": "john@example.com",
                "is_verified": true,
                "checked_at": "2024-01-15T10:45:00Z"
           }
        }
        ```
    """

    data: VerificationStatusDataSchema
