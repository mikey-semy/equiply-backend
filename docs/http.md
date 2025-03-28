Теперь давайте проверим, как данные отправляются на сервер. Проблема может быть в том, что вы используете параметр data вместо json при отправке запроса. В aiohttp, если вы используете data, то данные отправляются как form-data, а не как JSON.

Давайте изменим метод post в классе BaseHttpClient:

async def post(self, url: str, headers: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
    """Выполняет POST запрос через контекстный менеджер"""
    # Используем json вместо data для автоматической сериализации
    async with self.request("POST", url, headers=headers, json=data) as req:
        return await req.execute()

Это должно решить проблему с отправкой данных в формате JSON.

Если это не поможет, попробуйте добавить дополнительное логирование в метод post класса BaseHttpClient:

async def post(self, url: str, headers: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
    """Выполняет POST запрос через контекстный менеджер"""
    self.logger.debug("Вызов метода post:")
    self.logger.debug(f"URL: {url}")
    self.logger.debug("Заголовки:")
    for header, value in headers.items():
        if header == "Authorization":
            self.logger.debug(f"  {header}: Api-Key ***")
        else:
            self.logger.debug(f"  {header}: {value}")
    
    self.logger.debug("Данные:")
    formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
    for line in formatted_data.split('\n'):
        self.logger.debug(f"  {line}")
    
    # Используем json вместо data для автоматической сериализации
    async with self.request("POST", url, headers=headers, json=data) as req:
        return await req.execute()

Это поможет вам увидеть, какие данные отправляются на сервер и в каком формате.