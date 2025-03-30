from pydantic import EmailStr
from app.schemas.v1.base import CommonBaseSchema

class EmailMessageSchema(CommonBaseSchema):
    """
    Схема сообщения для отправки email

    Attributes:
        to_email (EmailStr): Email адрес получателя
        subject (str): Тема письма
        body (str): Содержимое письма
    """
    to_email: EmailStr
    subject: str
    body: str

class VerificationEmailSchema(EmailMessageSchema):
    """
    Схема для письма верификации

    Attributes:
        user_name (str): Имя пользователя для персонализации письма
        verification_token (str): Токен для верификации email
    """
    user_name: str
    verification_token: str

class PasswordResetEmailSchema(EmailMessageSchema):
    """
    Схема для письма сброса пароля

    Attributes:
        user_name (str): Имя пользователя для персонализации письма
        reset_token (str): Токен для сброса пароля
    """
    user_name: str
    reset_token: str

class RegistrationSuccessEmailSchema(EmailMessageSchema):
    """
    Схема для письма об успешной регистрации

    Attributes:
        user_name (str): Имя пользователя для персонализации письма
    """
    user_name: str