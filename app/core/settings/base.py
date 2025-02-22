from pydantic_settings import BaseSettings

from app.core.lifespan import lifespan

from .routes import RouteConfig
from .paths import PathSettings

class BaseAppSettings(BaseSettings):
    """
    Базовые настройки приложения

    """

    TITLE: str = "CRM"
    DESCRIPTION: str = "CRM - это система управления взаимоотношениями с клиентами."
    VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_VERSIONS: list[str] = ["v1"]
    ROUTES: dict[str, RouteConfig] = {
        "main": RouteConfig("", ["Main"])

    }

    @property
    def app_params(self) -> dict:
        """
        Параметры для инициализации FastAPI приложения.

        Returns:
            Dict с настройками FastAPI
        """
        return {
            "title": self.TITLE,
            "description": self.DESCRIPTION,
            "version": self.VERSION,
            "swagger_ui_parameters": {"defaultModelsExpandDepth": -1},
            "root_path": "",
            "lifespan": lifespan,
        }

    @property
    def uvicorn_params(self) -> dict:
        """
        Параметры для запуска uvicorn сервера.

        Returns:
            Dict с настройками uvicorn
        """
        return {
            "host": self.HOST,
            "port": self.PORT,
            "proxy_headers": True,
            "log_level": "debug",
        }

    model_config = PathSettings.model_config
