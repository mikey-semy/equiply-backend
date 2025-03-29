import logging
from typing import Dict, TypeVar

from app.core.exceptions import OAuthUserDataError
from app.schemas import (GoogleUserDataSchema, VKUserDataSchema,
                         YandexUserDataSchema)

T = TypeVar("T", YandexUserDataSchema, GoogleUserDataSchema, VKUserDataSchema)


class BaseOAuthHandler:
    """Базовый обработчик данных от OAuth провайдеров"""

    def __init__(self, provider: str):
        self.provider = provider
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{provider}")

    def validate_required_fields(self, data: dict, fields: list) -> None:
        """Проверка обязательных полей"""
        missing = [f for f in fields if not data.get(f)]
        if missing:
            raise OAuthUserDataError(
                self.provider, f"Отсутствуют обязательные поля: {', '.join(missing)}"
            )

    def clean_name(self, name: str | None) -> str | None:
        """Очистка и валидация имени"""
        if not name:
            return None
        return name.strip()[:50]  # Ограничение из RegistrationSchema


class YandexHandler(BaseOAuthHandler):
    async def __call__(self, data: dict) -> YandexUserDataSchema:
        """
        Обработка данных пользователя от Яндекса.

        Преобразует "сырые" данные от Яндекс API в унифицированный формат.
        Проверяет наличие обязательного поля default_email.

        Args:
            user_data: Словарь с данными от Яндекс API
                - id: Идентификатор пользователя
                - default_email: Основной email (обязательное поле)
                - first_name: Имя пользователя
                - last_name: Фамилия
                - avatar: URL аватара
                - login: Логин
                - emails: Список всех email адресов
                - psuid: ID в системе Яндекс

        Returns:
            YandexUserData: Структурированные данные пользователя

        Raises:
            OAuthUserDataError: Если отсутствует default_email
        """
        self.validate_required_fields(data, ["id", "default_email"])

        avatar = None
        if data.get("is_avatar_empty") is False and data.get("default_avatar_id"):
            # Яндекс возвращает аватар в формате "//avatars.yandex.net/get-yapic/ID/islands-200"
            avatar_id = data.get("default_avatar_id")
            avatar = f"https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200"
        elif data.get("avatar"):
            avatar = data.get("avatar")

        self.logger.debug("Аватар пользователя (yandex handler): %s", avatar)

        return YandexUserDataSchema(
            id=str(data["id"]),
            email=data["default_email"],
            first_name=self.clean_name(data.get("first_name")),
            last_name=self.clean_name(data.get("last_name")),
            avatar=avatar,
            default_email=data["default_email"],
            login=data.get("login"),
            emails=data.get("emails", []),
            psuid=data.get("psuid"),
        )


class GoogleHandler(BaseOAuthHandler):
    async def __call__(self, data: dict) -> GoogleUserDataSchema:
        """
        Обработка данных пользователя от Google.

        Преобразует данные от Google API в унифицированный формат.
        Обрабатывает специфичные для Google поля given_name и family_name.

        Args:
            user_data: Словарь с данными от Google API
                - id: Идентификатор пользователя
                - email: Email пользователя
                - verified_email: Флаг верификации email
                - given_name: Имя
                - family_name: Фамилия
                - picture: URL фото профиля

        Returns:
            GoogleUserData: Структурированные данные пользователя
        """
        self.validate_required_fields(data, ["id", "email"])

        avatar = data.get("picture")
        if avatar and "?sz=" in avatar:
            # Заменяем размер на больший, если он указан
            avatar = avatar.split("?sz=")[0] + "?sz=200"

        self.logger.debug("Аватар пользователя (google handler): %s", avatar)

        return GoogleUserDataSchema(
            id=str(data["id"]),
            email=data.get("email"),
            first_name=self.clean_name(data.get("given_name")),
            last_name=self.clean_name(data.get("family_name")),
            avatar=avatar,
            verified_email=bool(data.get("verified_email")),
            given_name=data.get("given_name"),
            family_name=data.get("family_name"),
            picture=data.get("picture"),
        )


class VKHandler(BaseOAuthHandler):
    async def __call__(self, data: dict) -> VKUserDataSchema:
        """
        Обработка данных пользователя от VK.

        Преобразует данные от VK API в унифицированный формат.
        Проверяет наличие обязательных полей user и user_id.
        Логирует предупреждение если отсутствует email.

        Args:
            user_data: Словарь с данными от VK API
                - user: Объект с данными пользователя
                    - user_id: ID пользователя (обязательное)
                    - email: Email пользователя
                    - first_name: Имя
                    - last_name: Фамилия
                    - avatar: URL фото
                    - phone: Номер телефона

        Returns:
            VKUserData: Структурированные данные пользователя

        Raises:
            OAuthUserDataError: Если отсутствуют данные пользователя или user_id
        """
        user = data.get("user", {})
        self.validate_required_fields(user, ["user_id", "email"])

        self.logger.debug("Аватар пользователя (vk handler): %s", avatar)
        avatar = None
        if user.get("avatar"):
            avatar = user.get("avatar")
        elif user.get("photo_max_orig"):
            avatar = user.get("photo_max_orig")
        elif user.get("photo_200"):
            avatar = user.get("photo_200")
        elif user.get("photo"):
            avatar = user.get("photo")

        return VKUserDataSchema(
            id=str(user["user_id"]),
            email=user.get("email"),
            first_name=self.clean_name(user.get("first_name")),
            last_name=self.clean_name(user.get("last_name")),
            avatar=avatar,
            phone=user.get("phone"),
            user_id=str(user["user_id"]),
        )


# Маппинг провайдеров к функциям
PROVIDER_HANDLERS: Dict[str, BaseOAuthHandler] = {
    "yandex": YandexHandler("yandex"),
    "google": GoogleHandler("google"),
    "vk": VKHandler("vk"),
}
