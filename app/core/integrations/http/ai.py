from app.core.exceptions import AIAuthError, AICompletionError
from app.core.settings import settings
from app.schemas import AIRequestSchema, AIResponseSchema, ResultSchema

from .base import BaseHttpClient


class AIHttpClient(BaseHttpClient):
    """
    Класс для работы с API Yandex
    """

    async def get_completion(self, chat_request: AIRequestSchema) -> AIResponseSchema:
        """
        Получение ответа от Yandex API

        Args:
            chat_request: Запрос к API

        Returns:
            AIResponseSchema: Ответ от API

        Raises:
            HTTPException: При ошибках запроса
        """
        headers = {
            "Authorization": f"Api-Key {settings.YANDEX_API_KEY.get_secret_value()}",
            "Content-Type": "application/json",
            "x-data-logging-enabled": "false",
        }

        if not settings.YANDEX_API_KEY.get_secret_value():
            raise AIAuthError("API ключ не задан")

        if not chat_request.modelUri:
            chat_request.modelUri = settings.yandex_model_uri

        try:
            request_data = chat_request.model_dump(by_alias=True)
            for msg in request_data["messages"]:
                if hasattr(msg["role"], "value"):
                    msg["role"] = msg["role"].value
            
             # Преобразуем maxTokens в число, если это строка
            if "completionOptions" in request_data and "maxTokens" in request_data["completionOptions"]:
                try:
                    request_data["completionOptions"]["maxTokens"] = int(request_data["completionOptions"]["maxTokens"])
                except (ValueError, TypeError):
                    pass
                
            # Подробное логирование запроса
            self.logger.debug("Отправка запроса к Yandex API:")
            self.logger.debug(f"URL: {settings.YANDEX_API_URL}")
            self.logger.debug("Заголовки:")
            for header, value in headers.items():
                if header == "Authorization":
                    self.logger.debug(f"  {header}: Api-Key ***")
                else:
                    self.logger.debug(f"  {header}: {value}")

            self.logger.debug("Тело запроса:")
            formatted_data = json.dumps(request_data, indent=2, ensure_ascii=False)
            for line in formatted_data.split('\n'):
                self.logger.debug(f"  {line}")

            response = await self.post(
                url=settings.YANDEX_API_URL, headers=headers, data=request_data
            )

            # Подробное логирование ответа
            self.logger.debug("Получен ответ от Yandex API:")
            formatted_response = json.dumps(response, indent=2, ensure_ascii=False)
            for line in formatted_response.split('\n'):
                self.logger.debug(f"  {line}")

            if not isinstance(response, dict):
                raise AICompletionError("Невалидный ответ от API")

            if "error" in response:
                raise AICompletionError(response["error"])

            result_data = response.get("result", {})

            if not all(
                key in result_data for key in ["alternatives", "usage", "modelVersion"]
            ):
                self.logger.error("Неверная структура ответа: %s", response)
                raise AICompletionError("Неверная структура ответа от API")

            return AIResponseSchema(success=True, result=ResultSchema(**result_data))

        except Exception as e:
            self.logger.error("Ошибка при запросе к API Yandex: %s", str(e))
            raise AICompletionError(str(e))
