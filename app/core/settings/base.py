from pydantic_settings import BaseSettings
from .routes import RouteConfig
from .paths import PathSettings

class BaseAppSettings(BaseSettings):
    """Базовые настройки приложения"""
    TITLE: str = "CRM"
    DESCRIPTION: str = "CRM - это система управления взаимоотношениями с клиентами."
    VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    API_VERSIONS = ["v1"]  # Поддерживаемые версии API

    ROUTES: dict[str, RouteConfig] = {
        "main": RouteConfig("", ["Main"]),
        # ...добавьте другие сервисы
    }

    model_config = PathSettings.model_config
