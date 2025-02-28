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
        
        # Используем непосредственно record.msg вместо getMessage()
        message = record.msg if record.msg is not None else ""
        
        # Форматируем сообщение с эмодзи
        formatted_message = f"{emoji}  {message}"

        extra_attrs = self.get_extra_attrs(record)
        extra_msg = f"\033[33m[extra: {extra_attrs}]{self.RESET}" if extra_attrs else ""

        # Используем непосредственно форматирование строки, если settings недоступны
        try:
            pretty_format = getattr(settings.logging, "PRETTY_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            base_msg = pretty_format % {
                "asctime": self.format_timestamp(record),
                "name": record.name,
                "levelname": f"{color}{record.levelname}{self.RESET}",
                "message": formatted_message
            }
        except (AttributeError, TypeError):
            # Если settings недоступны или формат неправильный, используем запасной вариант
            base_msg = f"{self.format_timestamp(record)} - {record.name} - {color}{record.levelname}{self.RESET} - {formatted_message}"

        return f"{base_msg} {extra_msg}" if extra_msg else base_msg

class CustomJsonFormatter(JsonFormatter, TimestampMixin):
    """
    Класс для форматирования логов в виде JSON.

    Methods:
        format(record): Форматирование записи лога в виде JSON.
    """
    def format(self, record):
        """
        Форматирование записи лога в виде JSON.

        Args:
            record (logging.LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка лога в формате JSON.
        """
        # Используем непосредственно record.msg вместо getMessage()
        message = record.msg if record.msg is not None else ""
        
        # Создаем базовый словарь с данными лога
        log_data = {
            "timestamp": self.format_timestamp(record),
            "level": record.levelname,
            "name": record.name,
            "module": record.module,
            "function": record.funcName, 
            "message": message
        }
        
        # Добавляем дополнительные атрибуты
        extra_attrs = self.get_extra_attrs(record)
        if extra_attrs:
            log_data["extra"] = extra_attrs
            
        # Если есть исключение, добавляем его
        if hasattr(record, "exc_info") and record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Пытаемся обогатить данные из settings.logging.JSON_FORMAT, если доступно
        try:
            json_format = getattr(settings.logging, "JSON_FORMAT", {})
            if isinstance(json_format, dict):
                for key, value in json_format.items():
                    if key not in log_data:  # Не переопределяем уже установленные поля
                        if isinstance(value, str):
                            log_data[key] = value % {
                                "levelname": record.levelname,
                                "module": record.module,
                                "funcName": record.funcName,
                                "message": message
                            }
                        else:
                            log_data[key] = value
        except (AttributeError, TypeError):
            # Если settings недоступны или формат неправильный, используем только базовые данные
            pass

        return json.dumps(log_data, ensure_ascii=False)