"""
Модуль для работы с куками аутентификации.

Предоставляет класс CookieManager для установки, чтения и удаления
куков с токенами аутентификации. Обеспечивает безопасную работу
с куками через HttpOnly, Secure и SameSite флаги.
"""

import logging
from typing import Optional

from fastapi import Response

from app.core.settings import settings

logger = logging.getLogger(__name__)


class CookieManager:
    """
    Класс для управления куками аутентификации.

    Предоставляет статические методы для установки, чтения и удаления
    куков с токенами. Использует настройки безопасности из конфигурации.

    Methods:
        set_auth_cookies: Устанавливает куки с токенами аутентификации
        clear_auth_cookies: Очищает куки с токенами
        set_access_token_cookie: Устанавливает куку с access токеном
        set_refresh_token_cookie: Устанавливает куку с refresh токеном
        clear_access_token_cookie: Очищает куку с access токеном
        clear_refresh_token_cookie: Очищает куку с refresh токеном
    """

    # Константы для ключей куков
    ACCESS_TOKEN_KEY = "access_token"
    REFRESH_TOKEN_KEY = "refresh_token"

    @staticmethod
    def set_auth_cookies(
        response: Response, access_token: str, refresh_token: str
    ) -> None:
        """
        Устанавливает куки с токенами аутентификации.

        Устанавливает как access, так и refresh токены в отдельные куки
        с соответствующими настройками безопасности и временем жизни.

        Args:
            response: HTTP ответ для установки куков
            access_token: Access токен для установки
            refresh_token: Refresh токен для установки

        Example:
            ```python
            response = Response()
            CookieManager.set_auth_cookies(response, access_token, refresh_token)
            ```
        """
        CookieManager.set_access_token_cookie(response, access_token)
        CookieManager.set_refresh_token_cookie(response, refresh_token)

        logger.debug(
            "Установлены куки с токенами аутентификации",
            extra={
                "access_token_length": len(access_token),
                "refresh_token_length": len(refresh_token),
            },
        )

    @staticmethod
    def set_access_token_cookie(response: Response, access_token: str) -> None:
        """
        Устанавливает куку с access токеном.

        Args:
            response: HTTP ответ для установки куки
            access_token: Access токен для установки
        """
        response.set_cookie(
            key=CookieManager.ACCESS_TOKEN_KEY,
            value=access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/",
        )

        logger.debug("Установлена кука с access токеном")

    @staticmethod
    def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
        """
        Устанавливает куку с refresh токеном.

        Refresh токен устанавливается только для endpoint'а обновления токенов
        для дополнительной безопасности.

        Args:
            response: HTTP ответ для установки куки
            refresh_token: Refresh токен для установки
        """
        response.set_cookie(
            key=CookieManager.REFRESH_TOKEN_KEY,
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/",#path="/api/v1/auth/refresh",  # Только для refresh endpoint
        )

        logger.debug("Установлена кука с refresh токеном")

    @staticmethod
    def clear_auth_cookies(response: Response) -> None:
        """
        Очищает все куки с токенами аутентификации.

        Удаляет как access, так и refresh токены из куков браузера.

        Args:
            response: HTTP ответ для очистки куков

        Example:
            ```python
            response = Response()
            CookieManager.clear_auth_cookies(response)
            ```
        """
        CookieManager.clear_access_token_cookie(response)
        CookieManager.clear_refresh_token_cookie(response)

        logger.debug("Очищены куки с токенами аутентификации")

    @staticmethod
    def clear_access_token_cookie(response: Response) -> None:
        """
        Очищает куку с access токеном.

        Args:
            response: HTTP ответ для очистки куки
        """
        response.delete_cookie(
            key=CookieManager.ACCESS_TOKEN_KEY,
            path="/",
            domain=settings.COOKIE_DOMAIN,
        )

        logger.debug("Очищена кука с access токеном")

    @staticmethod
    def clear_refresh_token_cookie(response: Response) -> None:
        """
        Очищает куку с refresh токеном.

        Args:
            response: HTTP ответ для очистки куки
        """
        response.delete_cookie(
            key=CookieManager.REFRESH_TOKEN_KEY,
            path="/api/v1/auth/refresh",
            domain=settings.COOKIE_DOMAIN,
        )

        logger.debug("Очищена кука с refresh токеном")

    @staticmethod
    def set_verification_cookie(
        response: Response, verification_token: str, max_age: Optional[int] = None
    ) -> None:
        """
        Устанавливает куку с токеном верификации email.

        Используется для временного хранения токена верификации
        в процессе подтверждения email адреса.

        Args:
            response: HTTP ответ для установки куки
            verification_token: Токен верификации email
            max_age: Время жизни куки в секундах (по умолчанию из настроек)
        """
        if max_age is None:
            max_age = settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60

        response.set_cookie(
            key="verification_token",
            value=verification_token,
            max_age=max_age,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/api/v1/auth/verify",
        )

        logger.debug("Установлена кука с токеном верификации")

    @staticmethod
    def clear_verification_cookie(response: Response) -> None:
        """
        Очищает куку с токеном верификации.

        Args:
            response: HTTP ответ для очистки куки
        """
        response.delete_cookie(
            key="verification_token",
            path="/api/v1/auth/verify",
            domain=settings.COOKIE_DOMAIN,
        )

        logger.debug("Очищена кука с токеном верификации")

    @staticmethod
    def get_cookie_settings() -> dict:
        """
        Возвращает текущие настройки куков для отладки.

        Returns:
            dict: Словарь с настройками куков
        """
        return {
            "secure": settings.COOKIE_SECURE,
            "samesite": settings.COOKIE_SAMESITE,
            "domain": settings.COOKIE_DOMAIN,
            "access_token_expire": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token_expire": settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        }
