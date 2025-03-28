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

        if data := self.kwargs.get("data"):
            self.logger.debug("Request body: %s", json.dumps(data, indent=2))
            self.kwargs["data"] = {k: v for k, v in data.items() if v is not None}

        return self._client

    async def execute(self) -> Dict[str, Any]:
        """Выполняет HTTP запрос"""
        async with self._client.request(
            self.method, self.url, **self.kwargs
        ) as response:
            try:
                # Сначала получаем текст ответа
                response_text = await response.text()
                self.logger.debug(f"Response status: {response.status}")
                self.logger.debug(f"Response text: {response_text}")
            
                # Затем пытаемся распарсить JSON
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON: {e}, raw text: {response_text}")
                    return {"error": f"Invalid JSON response: {str(e)}", "raw_text": response_text}
            except Exception as e:
                self.logger.error(f"Error processing response: {str(e)}")
                return {"error": f"Error processing response: {str(e)}"}
