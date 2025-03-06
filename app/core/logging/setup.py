import logging
import os
from pathlib import Path

from app.core.settings import settings

from .formatters import CustomJsonFormatter, PrettyFormatter


def setup_logging():
    root = logging.getLogger()

    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    log_config = settings.logging.to_dict()

    # Консольный хендлер с pretty/json форматом из конфига
    console_formatter = (
        CustomJsonFormatter() if settings.logging.LOG_FORMAT == "json" else PrettyFormatter()
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    # Файловый хендлер всегда с JSON форматом
    if log_config.get("filename"):
        log_path = Path(log_config["filename"])

        # Создаем директорию с нужными правами
        if not log_path.parent.exists():
            os.makedirs(str(log_path.parent), exist_ok=True)

        file_handler = logging.FileHandler(
            filename=log_config["filename"],
            mode=log_config.get("filemode", "a"),
            encoding=log_config.get("encoding", "utf-8"),
        )
        file_handler.setFormatter(CustomJsonFormatter())
        root.addHandler(file_handler)

    root.setLevel(log_config.get("level", logging.INFO))

    for logger_name in [
        "python_multipart",
        "sqlalchemy.engine",
        "passlib",
        "aio_pika",
        "aiormq",
    ]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
