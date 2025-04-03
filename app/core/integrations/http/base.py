import json
import logging
from typing import Any, Dict, Optional

import aiohttp


class RequestContextManager:
    """
    Контекстный менеджер для HTTP запросов.

    Args:
        client (BaseHttpClient): HTTP клиент
        method (str): HTTP метод (GET, POST и т.д.)
        url (str): URL для запроса
        **kwargs: Дополнительные параметры запроса (headers, data и т.д.)

    Returns:
        RequestContextManager: Контекст для выполнения запроса

    Usage:
        async with client.request('GET', 'https://api.example.com') as req:
            data = await req.execute()

    Examples:
        # Простой GET запрос
        async with client.request('GET', url) as req:
            data = await req.execute()

        # POST запрос с данными
        async with client.request('POST', url, data={'key': 'value'}) as req:
            data = await req.execute()
    """

    def __init__(self, client: "BaseHttpClient", method: str, url: str, **kwargs):
        self.client = client
        self.method = method
        self.url = url
        self.kwargs = kwargs
        self.logger = client.logger

    async def __aenter__(self) -> "RequestContextManager":
        """
        Подготовка запроса.

        Returns:
            RequestContextManager: Подготовленный контекст запроса
        """
        self.session = await self.client._get_session()
        self.logger.debug(f"{self.method} запрос к {self.url}")

        if data := self.kwargs.get("data"):
            self.logger.debug("Request body: %s", json.dumps(data, indent=2))
            self.kwargs["data"] = {k: v for k, v in data.items() if v is not None}

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Закрытие сессии после выполнения запроса"""
        await self.client.close()

    async def execute(self) -> Dict[str, Any]:
        """
        Выполнение HTTP запроса.

        Returns:
            Dict[str, Any]: JSON ответ от сервера

        Raises:
            aiohttp.ClientError: При ошибках HTTP запроса
            json.JSONDecodeError: При ошибках декодирования JSON
        """
        async with self.session.request(
            self.method, self.url, **self.kwargs
        ) as response:

            # Получаем текст ответа
            response_text = await response.text()

            # Пробуем распарсить JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                self.logger.error(
                    f"Failed to parse JSON: {e}, raw text: {response_text}"
                )
                # Возвращаем ошибку в формате, который можно обработать
                return {
                    "error": f"Invalid JSON response: {str(e)}",
                    "raw_text": response_text,
                    "status_code": response.status,
                }


class BaseHttpClient:
    """
    Базовый HTTP клиент с поддержкой контекстного менеджера.

    Usage:
        client = BaseHttpClient()
        async with client.request('GET', url) as req:
            data = await req.execute()
    """

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None
            self.logger.debug("Сессия закрыта")

    def request(self, method: str, url: str, **kwargs) -> "RequestContextManager":
        """Создает контекст для выполнения запроса"""
        return RequestContextManager(self, method, url, **kwargs)

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Выполняет GET запрос через контекстный менеджер"""
        async with self.request("GET", url, **kwargs) as req:
            return await req.execute()

    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Выполняет POST запрос через контекстный менеджер"""
        async with self.request("POST", url, **kwargs) as req:
            return await req.execute()
