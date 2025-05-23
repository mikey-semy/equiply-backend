from app.schemas.v1.base import BaseResponseSchema


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
        message: Сообщение об успешной авторизации
    """
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    message: str = "Авторизация успешна"


class LogoutResponseSchema(BaseResponseSchema):
    """
    Схема ответа для выхода из системы.

    Отправляется клиенту после успешного завершения сессии и выхода пользователя из системы.

    Attributes:
        message: Информационное сообщение о результате операции.
    """

    message: str = "Выход выполнен успешно!"


class PasswordResetResponseSchema(BaseResponseSchema):
    """
    Схема ответа на запрос сброса пароля.

    Отправляется после успешной обработки запроса на сброс пароля.

    Attributes:
        message: Информационное сообщение о результате операции и дальнейших действиях.
    """

    message: str = "Инструкции по сбросу пароля отправлены на ваш email"


class PasswordResetConfirmResponseSchema(BaseResponseSchema):
    """
    Схема ответа на установку нового пароля.

    Отправляется пользователю после успешного изменения пароля.

    Attributes:
        message: Информационное сообщение о результате операции.
    """

    message: str = "Пароль успешно изменен"
