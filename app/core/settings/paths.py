import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class PathSettings:
    """Конфигурация путей к файлам настроек."""

    TEMPLATES_DIR: Path = Path(__file__).parent.parent.parent / 'templates'
    EMAIL_TEMPLATES_DIR: Path = TEMPLATES_DIR / 'mail'

    @staticmethod
    def get_env_file_and_type() -> tuple[Path, str]:
        """
        Определяет путь к файлу с переменными окружения и тип окружения.

        Returns:
            tuple[Path, str]: Путь к файлу с переменными окружения и тип окружения (dev/prod/test/custom)
        """
        ENV_FILE = Path(".env")
        DEV_ENV_FILE = Path(".env.dev")

        # Определяем конфигурацию
        if os.getenv("ENV_FILE"):
            env_path = Path(os.getenv("ENV_FILE"))
            if ".env.test" in str(env_path):
                env_type = "test"
            else:
                env_type = "custom"
        elif DEV_ENV_FILE.exists():
            env_path = DEV_ENV_FILE
            env_type = "dev"
        else:
            env_path = ENV_FILE
            env_type = "prod"

        logger.info("Запуск в режиме: %s", env_type.upper())
        logger.info("Конфигурация: %s", env_path)

        return env_path, env_type
