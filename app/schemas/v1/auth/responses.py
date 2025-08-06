"""
Схемы ответов для аутентификации.

Содержит Pydantic схемы для исходящих данных endpoints аутентификации.
Все схемы следуют единому формату: {success, message, data}.
"""

from app.schemas.v1.base import BaseResponseSchema

from .base import (LogoutDataSchema, PasswordResetConfirmDataSchema,
                   PasswordResetDataSchema, TokenDataSchema)


class TokenResponseSchema(BaseResponseSchema):
    """
    Схема ответа с токеном доступа

    Swagger UI ожидает строго определенный формат ответа для OAuth2 password flow
    (access_token и token_type обязательны, другие поля игнорируются)

    Docs:
        https://swagger.io/docs/specification/authentication/oauth2/
        (Из РФ зайти можно только через VPN - санкции)

        https://developer.zendesk.com/api-reference/sales-crm/authentication/requests/#token-request

    Attributes:
        access_token: Основной токен для доступа к защищенным ресурсам.
        refresh_token: Токен для получения нового access_token без повторной аутентификации пользователя
        token_type: Тип токена.
        expires_in: Время жизни токена в секундах.
        message: Сообщение об успешной авторизации

    Example:
        {
            "success": true,
            "message": "Аутентификация успешна",
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
            "token_type": "Bearer",
            "expires_in": 1800
        }
    """

    access_token: None | str
    refresh_token: None | str
    token_type: str = "Bearer"
    expires_in: int
    message: str = "Авторизация успешна"


class LogoutResponseSchema(BaseResponseSchema):
    """
    Схема ответа при выходе из системы.

    Возвращается при успешном завершении пользовательской сессии.
    Подтверждает инвалидацию токенов и очистку кэша.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Сообщение о результате выхода
        data: Данные о времени выхода

    Example:
        {
            "success": true,
            "message": "Выход выполнен успешно",
            "data": {
                "logged_out_at": "2024-01-15T10:30:00Z"
            }
        }
    """

    data: LogoutDataSchema


class PasswordResetResponseSchema(BaseResponseSchema):
    """
    Схема ответа на запрос восстановления пароля.

    Возвращается при успешной отправке письма с инструкциями по сбросу пароля.
    Содержит информацию о параметрах восстановления.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Сообщение о результате запроса
        data: Данные о восстановлении пароля

    Example:
        {
            "success": true,
            "message": "Инструкции по сбросу пароля отправлены на ваш email",
            "data": {
                "email": "user@example.com",
                "expires_in": 1800
            }
        }
    """

    data: PasswordResetDataSchema


class PasswordResetConfirmResponseSchema(BaseResponseSchema):
    """
    Схема ответа на подтверждение сброса пароля.

    Возвращается при успешном изменении пароля по токену восстановления.
    Подтверждает завершение процедуры сброса пароля.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Сообщение о результате изменения
        data: Данные об изменении пароля

    Example:
        {
            "success": true,
            "message": "Пароль успешно изменен",
            "data": {
                "password_changed_at": "2024-01-15T10:35:00Z"
            }
        }
    """

    data: PasswordResetConfirmDataSchema


# Специальная схема для OAuth2 совместимости
class OAuth2TokenResponseSchema(BaseResponseSchema):
    """
    Схема ответа с токеном доступа для OAuth2 совместимости.

    Swagger UI ожидает строго определенный формат ответа для OAuth2 password flow.
    Поля access_token и token_type обязательны на верхнем уровне.

    Docs:
        https://swagger.io/docs/specification/authentication/oauth2/
        https://tools.ietf.org/html/rfc6749#section-5.1

    Attributes:
        access_token: Основной токен для доступа к защищенным ресурсам
        refresh_token: Токен для получения нового access_token
        token_type: Тип токена (Bearer)
        expires_in: Время жизни токена в секундах
        success: Статус успешности операции
        message: Сообщение об успешной авторизации
        data: Дублирование данных токенов для единообразия API
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    data: TokenDataSchema
