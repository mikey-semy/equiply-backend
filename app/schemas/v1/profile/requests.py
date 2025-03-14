from pydantic import Field, EmailStr, field_validator
from app.core.security.password import BasePasswordValidator
from app.schemas.v1.base import BaseRequestSchema

class ProfileUpdateSchema(BaseRequestSchema):
    """
    Схема для представления профиля пользователя.

    Args:
        username: Имя пользователя.
        email: Электронная почта пользователя.
        phone: Телефон пользователя.
    """

    username: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(description="Email пользователя")
    phone: str | None = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
class PasswordFormSchema(BaseRequestSchema):
    """
    Схема для формы изменения пароля.

    Attributes:
        old_password (str): Текущий пароль пользователя.
        new_password (str): Новый пароль пользователя.
        confirm_password (str): Подтверждение нового пароля.
    """

    old_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(
        ...,
        description="Новый пароль (минимум 8 символов, заглавная и строчная буква, цифра, спецсимвол)",
        alias="new_password"
    )
    confirm_password: str = Field(..., description="Подтверждение нового пароля")

    @classmethod
    @field_validator('new_password')
    def validate_new_password(cls, v, info):
        """Проверяет сложность нового пароля."""
        validator = BasePasswordValidator()
        return validator.validate_password_strength(v)

    @classmethod
    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        """Проверяет, что новый пароль и подтверждение совпадают."""
        data = info.data
        if 'new_password' in data and v != data['new_password']:
            raise ValueError('Пароли не совпадают')
        return v
