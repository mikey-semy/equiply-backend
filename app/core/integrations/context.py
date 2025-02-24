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
    def __init__(self, client: BaseHttpClient, method: str, url: str, **kwargs):
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

        if data := self.kwargs.get('data'):
            self.logger.debug("Request body: %s", json.dumps(data, indent=2))
            self.kwargs['data'] = {k: v for k, v in data.items() if v is not None}

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
        async with self.session.request(self.method, self.url, **self.kwargs) as response:
            return await response.json()
