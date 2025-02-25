from pydantic_settings import SettingsConfigDict

# Базовая конфигурация для всех модулей
BASE_CONFIG = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    env_nested_delimiter="__",
    extra="allow"
)