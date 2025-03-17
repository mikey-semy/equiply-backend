import secrets
from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field


from app.schemas.v1.register.requests import RegistrationSchema

from app.schemas.v1.base import CommonBaseSchema


class OAuthProvider(str, Enum):
    """
    Наименования поддерживаемых OAuth провайдеры

    Чтобы получить, необходимо использовать .value например:
    OAuthProvider.YANDEX.value

    Пример использования:
    OAuthProvider.YANDEX.value == "yandex"
    """

    YANDEX = "yandex"
    GOOGLE = "google"
    VK = "vk"

class OAuthUserSchema(RegistrationSchema):
    """
    Схема создания пользователя через OAuth

    см. в RegistrationSchema
    """

    avatar: Optional[str] = None
    vk_id: Optional[int] = None
    google_id: Optional[str] = None
    yandex_id: Optional[int] = None


class OAuthConfigSchema(CommonBaseSchema):
    """
    Конфигурация OAuth провайдера

    Attributes:
        client_id: Идентификатор приложения
        client_secret: Секретный ключ приложения
        auth_url: URL для авторизации
        token_url: URL для получения токена
        user_info_url: URL для получения информации о пользователе
        scope: Область доступа
        callback_url: URL для перенаправления после авторизации (для провайдера)
    """

    client_id: str | int  # VK: client_id = id приложения >_<
    client_secret: str
    auth_url: str
    token_url: str
    user_info_url: str
    scope: str
    callback_url: str


class OAuthParamsSchema(CommonBaseSchema):
    """
    Базовый класс для OAuth параметров

    Attributes:
        response_type: Тип ответа (code)
        client_id: Идентификатор приложения
        redirect_uri: Путь для перенаправления после авторизации (для пользователя)
        scope: Область доступа

    """

    response_type: str = "code"
    client_id: str | int  # VK: client_id = id приложения >_<
    redirect_uri: str
    scope: str = ""


class VKOAuthParamsSchema(OAuthParamsSchema):
    """
    Класс для дополнительных параметров OAuth авторизации через VK

    Attributes:
        state: Строка состояния в виде случайного набора символов
        code_challenge: Значение code_verifier,
            преобразованное с помощью code_challenge_method и закодированное в base64
    """

    state: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    code_challenge: str
    code_challenge_method: str = "S256"

class OAuthUserDataSchema(CommonBaseSchema):
    """
    Базовый класс для данных пользователя OAuth

    Attributes:
        id: Идентификатор пользователя
        email: Электронная почта пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        avatar: Ссылка на аватар пользователя
    """

    id: str
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: Optional[str] = None


class YandexUserDataSchema(OAuthUserDataSchema):
    """
    Класс для данных пользователя OAuth через Яндекс

    Attributes:
        default_email: Основная электронная почта пользователя в Яндекс ID (у других обычно email)
        login: Логин пользователя
        emails: Список электронных почт пользователя
        psuid: Идентификатор пользователя в Яндекс ID
    """

    default_email: EmailStr
    login: str | None = None
    emails: list[EmailStr] | None = None
    psuid: str | None = None


class GoogleUserDataSchema(OAuthUserDataSchema):
    """
    Класс для данных пользователя OAuth через Google

    Attributes:
        email_verified: Флаг, указывающий, что электронная почта пользователя была подтверждена
        given_name: Имя пользователя
        family_name: Фамилия пользователя
        picture: Ссылка на аватар пользователя
    """

    verified_email: bool = False
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None


class VKUserDataSchema(OAuthUserDataSchema):
    """
    Класс для данных пользователя OAuth через VK

    Attributes:
        phone: Номер телефона пользователя
        user_id: Идентификатор пользователя
    """

    phone: str | None = None
    user_id: str | None = None


class OAuthTokenParamsSchema(CommonBaseSchema):
    """
    Класс для параметров OAuth авторизации (для получения токена)

    Attributes:
        grant_type: Тип запроса (authorization_code)
        redirect_uri: URL для callback (Путь для перенаправления после авторизации (для провайдера)
        code: Код авторизации
        client_id: Идентификатор приложения
        client_secret: Секретное слово приложения
    """

    grant_type: str = "authorization_code"
    redirect_uri: str
    code: str
    client_id: str
    client_secret: str | None = None


class VKOAuthTokenParamsSchema(OAuthTokenParamsSchema):
    """
    Параметры для получения токена VK OAuth

    Attributes:
        grant_type: Тип запроса (authorization_code)
        code_verifier: Код подтверждения
        redirect_uri: URL для callback
        code: Код авторизации
        client_id: ID приложения VK
        client_secret: Секретный ключ приложения
        device_id: ID устройства (для получения токена из callback)
        state: Состояние для CSRF защиты (произвольная строка состояния)
    """

    code_verifier: str | None = None
    device_id: str
    state: str | None = None
