from aiologger import Logger
from aiologger.levels import LogLevel
from aiologger.handlers.files import AsyncFileHandler
from aiologger.handlers.streams import AsyncStreamHandler

from app.core.settings import settings

from .formatters import PrettyFormatter, CustomJsonFormatter

async def setup_logging():
    """
    Настраивает асинхронное логирование с помощью aiologger.

    Returns:
        Logger: Настроенный логгер с консольным и файловым хендлерами

    Features:
        - Поддержка JSON и человекочитаемого форматов
        - Цветной вывод в консоль с эмодзи
        - Ротация файлов логов
        - Асинхронная запись без блокировок
        - Дополнительные поля через extra
    """
    logger = Logger(name="app")

    # Очищаем существующие хендлеры
    logger.handlers.clear()

    log_format = getattr(settings, "LOG_FORMAT", "pretty")

    # Консольный хендлер
    console_handler = AsyncStreamHandler()
    console_formatter = CustomJsonFormatter() if log_format == "json" else PrettyFormatter()
    console_handler.formatter = console_formatter
    logger.handlers.append(console_handler)

    # Файловый хендлер
    log_file = getattr(settings, "LOG_FILE", None)
    if log_file:
        file_handler = AsyncFileHandler(
            filename=log_file,
            mode=getattr(settings, "FILE_MODE", "a"),
            encoding=getattr(settings, "ENCODING", "utf-8")
        )
        file_handler.formatter = CustomJsonFormatter()
        logger.handlers.append(file_handler)

    # Устанавливаем уровень логирования - ВАЖНО: Преобразуем строку в LogLevel
    log_level = getattr(settings, "LOG_LEVEL", "DEBUG")
    
    # Преобразуем строковый уровень логирования в объект LogLevel
    level_mapping = {
        "CRITICAL": LogLevel.CRITICAL,
        "FATAL": LogLevel.CRITICAL,
        "ERROR": LogLevel.ERROR,
        "WARNING": LogLevel.WARNING,
        "WARN": LogLevel.WARNING,
        "INFO": LogLevel.INFO,
        "DEBUG": LogLevel.DEBUG,
        "NOTSET": LogLevel.NOTSET
    }
    
    # Получаем LogLevel из строки, по умолчанию DEBUG
    logger.level = level_mapping.get(log_level.upper(), LogLevel.DEBUG)

    # Настройка уровней для сторонних логгеров
    for logger_name in [
        "python_multipart",
        "sqlalchemy.engine",
        "passlib",
        "aio_pika",
        "aiormq"
    ]:
        Logger.with_default_handlers(name=logger_name).level = "WARNING"

    return logger
