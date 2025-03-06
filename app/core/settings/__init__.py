from functools import lru_cache

from .settings import Settings


class Config(Settings):
    """
    Объединенная конфигурация приложения.
    Наследует все настройки из Settings.
    """

    def __init__(self, **kwargs):
        Settings.__init__(self, **kwargs)


@lru_cache
def get_config() -> Config:
    """
    Получение конфигурации приложения из кэша.
    """
    config_instance = Config()

    return config_instance


settings = get_config()

__all__ = ["settings"]
