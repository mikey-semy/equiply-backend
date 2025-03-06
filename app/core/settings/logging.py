import os
from pydantic_settings import BaseSettings

class LoggingSettings(BaseSettings):
    """Конфигурация логирования"""

    LOG_FORMAT: str = "pretty"
    LOG_FILE: str = "./logs/app.log" if os.name == "nt" else "/var/log/app.log"
    LEVEL: str = "DEBUG"
    MAX_BYTES: int = 10485760  # 10MB
    BACKUP_COUNT: int = 5
    ENCODING: str = "utf-8"
    FILE_MODE: str = "a"
    FILE_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    PRETTY_FORMAT: str = (
        "\033[1;36m%(asctime)s\033[0m - \033[1;32m%(name)s\033[0m - %(levelname)s - %(message)s"
    )

    JSON_FORMAT: dict = {
        "timestamp": "%(asctime)s",
        "level": "%(levelname)s",
        "module": "%(module)s",
        "function": "%(funcName)s",
        "message": "%(message)s",
    }

    def to_dict(self) -> dict:
        return {
            "level": self.LEVEL,
            "filename": self.LOG_FILE,
            "maxBytes": self.MAX_BYTES,
            "backupCount": self.BACKUP_COUNT,
            "encoding": self.ENCODING,
            "filemode": self.FILE_MODE,
            "format": self.PRETTY_FORMAT if self.LOG_FORMAT == "pretty" else None,
            "json_format": self.JSON_FORMAT if self.LOG_FORMAT == "json" else None,
            "force": True,
            "file_json": True,
        }
