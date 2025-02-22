from aiologger import Logger
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

    # Консольный хендлер
    console_handler = AsyncStreamHandler()
    console_formatter = CustomJsonFormatter() if settings.logging.LOG_FORMAT == "json" else PrettyFormatter()
    console_handler.formatter = console_formatter
    logger.handlers.append(console_handler)

    # Файловый хендлер
    if settings.logging.LOG_FILE:
        file_handler = AsyncFileHandler(
            filename=settings.logging.LOG_FILE,
            mode=settings.logging.FILE_MODE,
            encoding=settings.logging.ENCODING
        )
        file_handler.formatter = CustomJsonFormatter()
        logger.handlers.append(file_handler)

    logger.level = settings.logging.LEVEL

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
