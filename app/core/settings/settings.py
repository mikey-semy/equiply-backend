from functools import lru_cache
from pydantic_settings import BaseSettings
from .base import BaseAppSettings
from .logging import LoggingSettings
from .paths import PathSettings

class Settings(BaseSettings):
    """Объединенные настройки"""
    app: BaseAppSettings = BaseAppSettings()
    logging: LoggingSettings = LoggingSettings()
    paths: PathSettings = PathSettings()

    class Config:
        arbitrary_types_allowed = True

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

__all__ = ["settings"]
