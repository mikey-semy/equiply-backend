import os
from pathlib import Path
from pydantic_settings import BaseSettings

from .config import BASE_CONFIG

class PathSettings(BaseSettings):
    """Конфигурация путей проекта"""
    ENV_FILE: Path = Path(".env")
    DEV_ENV_FILE: Path = Path(".env.dev")
    TEST_ENV_FILE: Path = Path(".env.test")
    APP_DIR: Path = Path("app")
    ENV_PATH: Path = None

    def __init__(self):
        super().__init__()
        self.ENV_PATH = self._determine_env_path()
        self._log_env_info()

    def _determine_env_path(self) -> Path:
        if os.getenv("ENV_FILE"):
            return Path(os.getenv("ENV_FILE"))
        elif self.DEV_ENV_FILE.exists():
            return self.DEV_ENV_FILE
        return self.ENV_FILE

    def _log_env_info(self):
        env_type = self._get_env_type()
        # logger.info("\n🚀 Запуск в режиме: %s", env_type)
        # logger.info("📁 Конфигурация: %s", self.ENV_PATH)

    def _get_env_type(self) -> str:
        if os.getenv("ENV_FILE"):
            return "TEST" if self.TEST_ENV_FILE in str(self.ENV_PATH) else "CUSTOM"
        elif self.DEV_ENV_FILE.exists():
            return "DEV"
        return "PROD"

    model_config = BASE_CONFIG
