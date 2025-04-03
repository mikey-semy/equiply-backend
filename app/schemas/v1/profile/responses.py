from app.schemas.v1.base import BaseResponseSchema

from .base import (AvatarDataSchema, PasswordDataSchema, ProfileSchema,
                   UsernameDataSchema)


class ProfileResponseSchema(BaseResponseSchema):
    """
    Схема ответа на успешное получения данных профиля
    """

    data: ProfileSchema
    message: str = "Данные профиля успешно получены"


class PasswordUpdateResponseSchema(BaseResponseSchema):
    """
    Схема ответа при успешном изменении пароля

    Attributes:
        message (str): Сообщение об успешной изменении пароля
    """

    message: str = "Пароль успешно изменен"


class AvatarResponseSchema(BaseResponseSchema):
    """
    Схема ответа с URL аватара пользователя.

    Attributes:
        data: Данные аватара
        message: Сообщение о успешном получении
    """

    data: AvatarDataSchema
    message: str = "URL аватара успешно получен"


class UsernameResponseSchema(BaseResponseSchema):
    """
    Ответ с сгенерированным именем пользователя

    Attributes:
        data: Данные сгенерированного имени пользователя
        message: Сообщение об успешном получении имени
    """

    data: UsernameDataSchema
    message: str = "Имя пользователя успешно сгенерировано"


class PasswordResponseSchema(BaseResponseSchema):
    """
    Ответ с сгенерированным паролем

    Attributes:
        data: Данные сгенерированного пароля
        message: Сообщение об успешном получении пароля
    """

    data: PasswordDataSchema
    message: str = "Пароль успешно сгенерирован"
