"""
Пакет конфигурации приложения.

Предоставляет централизованный доступ к настройкам всего приложения через единый объект settings.

Example:
    >>> from app.core.settings import settings
    >>> settings.database_dsn
    'sqlite+aiosqlite:///./test.db'
    >>> settings.docs_access
    True
    >>> settings.TITLE
    'Registration Service'
"""

from functools import lru_cache


from .settings import Settings


class Config(Settings):
    """
    Объединенная конфигурация приложения.
    Наследует все настройки из Settings.
    """

    pass


@lru_cache
def get_settings() -> Config:
    """
    Получение конфигурации приложения из кэша.
    """
    settings_instance = Config()

    return settings_instance


# def clear_config_cache():
# get_config.cache_clear()
# return get_config()

# config = clear_config_cache()

settings = get_settings()

__all__ = ["settings"]