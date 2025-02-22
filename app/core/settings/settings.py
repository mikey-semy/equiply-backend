import os
from typing import List
from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from .base import BaseAppSettings
from .logging import LoggingSettings
from .paths import PathSettings

class Settings(BaseSettings):
    """
    Настройки приложения

    """

    app: BaseAppSettings = BaseAppSettings()
    logging: LoggingSettings = LoggingSettings()
    paths: PathSettings = PathSettings()

    # Настройки доступа в docs/redoc
    DOCS_ACCESS: bool = True
    DOCS_USERNAME: str = "admin"
    DOCS_PASSWORD: SecretStr = "admin"

    # Настройки логирования
    LOG_FORMAT: str = "pretty"
    LOG_FILE: str = "./logs/app.log" if os.name == "nt" else "/var/log/app.log"
    LOG_LEVEL: str = "DEBUG"

    # Настройки базы данных
    DATABASE_DSN: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/crm"

    # Настройки AWS
    AWS_SERVICE: str = "s3"
    AWS_REGION: str = "ru-central1"
    AWS_ENDPOINT: str
    AWS_BUCKET: str = "crm-bucket"
    AWS_ACCESS_KEY: SecretStr
    AWS_SECRET_KEY: SecretStr

    # Настройки CORS
    ALLOW_ORIGINS: List[str] = []
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]
    class Config:
        """
        Конфигурация настроек

        Parameters:
            - arbitrary_types_allowed: True
                - Позволяет использовать произвольные типы данных в настройках.
        """
        arbitrary_types_allowed = True

    model_config = PathSettings.model_config

@lru_cache
def get_settings() -> Settings:
    """
    Возвращает экземпляр настроек приложения.

    Returns:
        Settings: Экземпляр настроек приложения.
    """
    return Settings()

settings = get_settings()

__all__ = ["settings"]
