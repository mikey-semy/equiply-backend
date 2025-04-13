"""
Модуль для работы с HTTP-подключениями.

Предоставляет классы для выполнения HTTP-запросов:
- HttpClient: Клиент для установки и управления HTTP-сессиями
- HttpContextManager: Контекстный менеджер для автоматического управления HTTP-запросами

Модуль использует aiohttp для асинхронного выполнения HTTP-запросов и
реализует базовые интерфейсы из модуля base.py.
"""
import json
from typing import Any, Dict

import aiohttp

from .base import BaseClient, BaseContextManager


class HttpClient(BaseClient):
    """
    HTTP клиент

    Реализует базовый класс BaseClient для управления HTTP-сессиями.
    Предоставляет возможность создания и закрытия HTTP-сессий.

    Attributes:
        _client (Optional[aiohttp.ClientSession]): Экземпляр HTTP-сессии
        logger (logging.Logger): Логгер для записи событий
    """

    async def connect(self) -> aiohttp.ClientSession:
        """
        Создает HTTP сессию

        Returns:
            aiohttp.ClientSession: Новая HTTP-сессия для выполнения запросов
        """
        self.logger.debug("Создание HTTP сессии...")
        self._client = aiohttp.ClientSession()
        return self._client

    async def close(self) -> None:
        """
        Закрывает HTTP сессию

        Безопасно закрывает активную HTTP-сессию, если она существует.
        """
        if self._client:
            self.logger.debug("Закрытие HTTP сессии...")
            await self._client.close()
            self._client = None


class HttpContextManager(BaseContextManager):
    """
    Контекстный менеджер для HTTP запросов

    Реализует контекстный менеджер для автоматического управления
    HTTP-запросами с подробным логированием.

    Attributes:
        http_client (HttpClient): Клиент для управления HTTP-сессией
        method (str): HTTP-метод запроса (GET, POST, etc.)
        url (str): URL для выполнения запроса
        kwargs (dict): Дополнительные параметры запроса
        logger (logging.Logger): Логгер для записи событий
    """

    def __init__(self, method: str, url: str, **kwargs) -> None:
        """
        Инициализация контекстного менеджера для HTTP-запросов.

        Args:
            method (str): HTTP-метод запроса
            url (str): URL для выполнения запроса
            **kwargs: Дополнительные параметры запроса (headers, data, json, etc.)
        """
        super().__init__()
        self.http_client = HttpClient()
        self.method = method
        self.url = url
        self.kwargs = kwargs

    async def connect(self) -> aiohttp.ClientSession:
        """
        Создает HTTP-сессию и логирует параметры запроса

        Returns:
            aiohttp.ClientSession: Настроенная HTTP-сессия
        """
        self._client = await self.http_client.connect()
        self.logger.debug("%s запрос к %s", self.method, self.url)

        # Логируем данные запроса, но не изменяем их
        if data := self.kwargs.get("data"):
            self.logger.debug("Данные запроса:")
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
            for line in formatted_data.split("\n"):
                self.logger.debug("  %s", line)

        return self._client

    async def execute(self) -> Dict[str, Any]:
        """
        Выполняет HTTP запрос

        Выполняет HTTP-запрос с подробным логированием всех этапов:
        заголовков, тела запроса и ответа.

        Returns:
            Dict[str, Any]: Результат запроса в формате JSON или словарь с ошибкой

        Note:
            В случае ошибки парсинга JSON возвращает словарь с ключами:
            - error: описание ошибки
            - raw_text: исходный текст ответа
        """
        try:
           # Логируем детали запроса перед отправкой
            is_debug = self.logger.isEnabledFor(10)  # DEBUG level

            if is_debug:
                self.logger.debug("Отправка %s запроса на URL: %s", self.method, self.url)
                self.logger.debug("Заголовки запроса: %s", self.kwargs.get('headers', {}))

                # Логируем тело запроса с отступами для лучшей читаемости
                if data := self.kwargs.get("data"):
                    self.logger.debug("Тело запроса (data):")
                    formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
                    for line in formatted_data.split("\n"):
                        self.logger.debug("  %s", line)

                if json_data := self.kwargs.get("json"):
                    self.logger.debug("Тело запроса (json):")
                    formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                    for line in formatted_json.split("\n"):
                        self.logger.debug("  %s", line)

            # Выполняем запрос
            async with self._client.request(
                self.method, self.url, **self.kwargs
            ) as response:
                # Получаем текст ответа
                response_text = await response.text()

                if is_debug:
                    self.logger.debug("Статус ответа: %s", response.status)

                    # Логируем заголовки ответа
                    self.logger.debug("Заголовки ответа:")
                    for header, value in response.headers.items():
                        self.logger.debug("  %s: %s", header, value)

                    # Логируем тело ответа
                    self.logger.debug("Тело ответа:")
                    if response_text:
                        # Пытаемся форматировать JSON для лучшей читаемости
                        try:
                            json_response = json.loads(response_text)
                            formatted_response = json.dumps(
                                json_response, indent=2, ensure_ascii=False
                            )
                            for line in formatted_response.split("\n"):
                                self.logger.debug("  %s", line)
                        except json.JSONDecodeError:
                            # Если не JSON, выводим как есть
                            for line in response_text.split("\n"):
                                self.logger.debug("  %s", line)
                    else:
                        self.logger.debug("  <пустой ответ>")

                # Пытаемся распарсить JSON
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError as e:
                    self.logger.error("Ошибка парсинга JSON: %s", e)
                    self.logger.error("Сырой текст ответа: %s", response_text)
                    return {
                        "error": f"Invalid JSON response: {str(e)}",
                        "raw_text": response_text,
                    }
        except Exception as e:
            self.logger.error("Ошибка при выполнении HTTP запроса: %s", str(e))
            return {"error": f"Error processing response: {str(e)}"}
