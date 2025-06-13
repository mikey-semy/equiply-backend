"""
Модуль безопасности приложения.

Содержит классы для работы с паролями, секретными ключами и токенами.

Example:
    >>> from app.core.security import TokenManager
    >>> token = TokenManager.generate_token(payload)

    >>> from app.core.security import PasswordHasher
    >>> hashed_password = PasswordHasher.hash_password("secretpassword")
"""

from .password import PasswordHasher
from .token import TokenManager
from .cookie import CookieManager

__all__ = ["PasswordHasher", "TokenManager", "CookieManager"]
