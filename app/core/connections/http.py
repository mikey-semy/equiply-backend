import json
from typing import Any, Dict

import aiohttp

from .base import BaseClient, BaseContextManager


class HttpClient(BaseClient):
    """HTTP клиент"""

    async def connect(self) -> aiohttp.ClientSession:
        """Создает HTTP сессию"""
        self.logger.debug("Создание HTTP сессии...")
        self._client = aiohttp.ClientSession()
        return self._client

    async def close(self) -> None:
        """Закрывает HTTP сессию"""
        if self._client:
            self.logger.debug("Закрытие HTTP сессии...")
            await self._client.close()
            self._client = None


class HttpContextManager(BaseContextManager):
    """Контекстный менеджер для HTTP запросов"""

    def __init__(self, method: str, url: str, **kwargs) -> None:
        super().__init__()
        self.http_client = HttpClient()
        self.method = method
        self.url = url
        self.kwargs = kwargs

    async def connect(self) -> aiohttp.ClientSession:
        self._client = await self.http_client.connect()
        self.logger.debug("%s запрос к %s", self.method, self.url)

        # Логируем данные запроса, но не изменяем их
        if data := self.kwargs.get("data"):
            self.logger.debug("Данные запроса:")
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
            for line in formatted_data.split("\n"):
                self.logger.debug(f"  {line}")

        return self._client

    async def execute(self) -> Dict[str, Any]:
        """Выполняет HTTP запрос"""
        try:
            # Логируем детали запроса перед отправкой
            self.logger.debug(f"Отправка {self.method} запроса на URL: {self.url}")
            self.logger.debug(f"Заголовки запроса: {self.kwargs.get('headers', {})}")

            # Логируем тело запроса с отступами для лучшей читаемости
            if data := self.kwargs.get("data"):
                self.logger.debug("Тело запроса (data):")
                formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
                for line in formatted_data.split("\n"):
                    self.logger.debug(f"  {line}")

            if json_data := self.kwargs.get("json"):
                self.logger.debug("Тело запроса (json):")
                formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                for line in formatted_json.split("\n"):
                    self.logger.debug(f"  {line}")

            # Выполняем запрос
            async with self._client.request(
                self.method, self.url, **self.kwargs
            ) as response:
                # Получаем текст ответа
                response_text = await response.text()
                self.logger.debug(f"Статус ответа: {response.status}")

                # Логируем заголовки ответа
                self.logger.debug("Заголовки ответа:")
                for header, value in response.headers.items():
                    self.logger.debug(f"  {header}: {value}")

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
                            self.logger.debug(f"  {line}")
                    except json.JSONDecodeError:
                        # Если не JSON, выводим как есть
                        for line in response_text.split("\n"):
                            self.logger.debug(f"  {line}")
                else:
                    self.logger.debug("  <пустой ответ>")

                # Пытаемся распарсить JSON
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Ошибка парсинга JSON: {e}")
                    self.logger.error(f"Сырой текст ответа: {response_text}")
                    return {
                        "error": f"Invalid JSON response: {str(e)}",
                        "raw_text": response_text,
                    }
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении HTTP запроса: {str(e)}")
            return {"error": f"Error processing response: {str(e)}"}
