
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

    def request(self, method: str, url: str, **kwargs) -> RequestContext:
        """Создает контекст для выполнения запроса"""
        return RequestContext(self, method, url, **kwargs)

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Выполняет GET запрос через контекстный менеджер"""
        async with self.request('GET', url, **kwargs) as req:
            return await req.execute()

    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Выполняет POST запрос через контекстный менеджер"""
        async with self.request('POST', url, **kwargs) as req:
            return await req.execute()
