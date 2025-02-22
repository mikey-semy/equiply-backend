from aiologger.formatters.base import Formatter
from aiologger.formatters.json import JsonFormatter
from datetime import datetime
import json
from app.core.settings import settings

class TimestampMixin:
    """
    Миксин для форматеров.

    Methods:
        format_timestamp(record): Форматирование временной метки в формате ISO 8601.
        get_extra_attrs(record): Получение дополнительных атрибутов из записи лога.
    """
    def format_timestamp(self, record):
        """
        Форматирование временной метки в формате ISO 8601.

        Args:
            record (logging.LogRecord): Запись лога.

        Returns:
            str: Отформатированная временная метка в формате ISO 8601:
                  YYYY-MM-DDTHH:MM:SS.sssZ.
        """
        return datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def get_extra_attrs(self, record):
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "asctime"
        }
        return {k: v for k, v in vars(record).items() if k not in standard_attrs}

class PrettyFormatter(Formatter, TimestampMixin):
    """
    Класс для форматирования логов в виде строки с использованием ANSI-цветов и эмодзи.

    Attributes:
        COLORS (dict): Цвета для разных уровней логов.
        EMOJIS (dict): Эмодзи для разных уровней логов.
        RESET (str): Код для сброса цвета.
        PRETTY_FORMAT (str): Формат для форматирования логов в виде строки с использованием ANSI-цветов и эмодзи.

    Methods:
        format(record): Форматирование записи лога в виде строки.
    """
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",   # Green
        "WARNING": "\033[33m", # Yellow
        "ERROR": "\033[31m",   # Red
        "CRITICAL": "\033[41m" # Red background
    }

    EMOJIS = {
        "DEBUG": "🔍",
        "INFO": "✨",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "💥"
    }

    RESET = "\033[0m"

    def format(self, record):
        """
        Форматирование записи лога в виде строки.

        Args:
            record (logging.LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка лога в формате Pretty:
                  YYYY-MM-DD HH:MM:SS.sssZ - NAME - LEVEL - MESSAGE [extra: {extra_attrs}].
        """
        emoji = self.EMOJIS.get(record.levelname, "")
        color = self.COLORS.get(record.levelname, "")

        extra_attrs = self.get_extra_attrs(record)
        extra_msg = f"\033[33m[extra: {extra_attrs}]{self.RESET}" if extra_attrs else ""

        base_msg = settings.logging.PRETTY_FORMAT % {
            "asctime": self.format_timestamp(record),
            "name": record.name,
            "levelname": f"{color}{record.levelname}{self.RESET}",
            "message": f"{emoji} {record.message}"
        }

        return f"{base_msg} {extra_msg}" if extra_msg else base_msg

class CustomJsonFormatter(JsonFormatter, TimestampMixin):
    """
    Класс для форматирования логов в виде JSON.

    Attributes:
        JSON_FORMAT (dict): Формат для JSON-строки лога.
    Methods:
        format(record): Форматирование записи лога в виде JSON.
    """
    def format(self, record):
        """
        Форматирование записи лога в виде JSON.

        Args:
            record (logging.LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка лога в формате JSON:
                  {"timestamp": "YYYY-MM-DD HH:MM:SS.sssZ", "level": "LEVEL", "module": "MODULE", "function": "FUNCTION", "message": "MESSAGE", "extra": {extra_attrs}}.

        """
        log_data = settings.logging.JSON_FORMAT.copy()

        log_data.update(self.get_extra_attrs(record))

        for key, value in log_data.items():
            if key == "timestamp":
                log_data[key] = self.format_timestamp(record)
            else:
                log_data[key] = value % {
                    "levelname": record.levelname,
                    "module": record.module,
                    "funcName": record.funcName,
                    "message": record.message
                }

        return json.dumps(log_data, ensure_ascii=False)
