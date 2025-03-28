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
                
            self.logger.debug("Request data: %s", request_data)

            response = await self.post(
                url=settings.YANDEX_API_URL, headers=headers, data=request_data
            )

            self.logger.debug("Raw response from API: %s", response)

            if not isinstance(response, dict):
                raise AICompletionError("Невалидный ответ от API")

            if "error" in response:
                raise AICompletionError(response["error"])

            result_data = response.get("result", {})

            if not all(
                key in result_data for key in ["alternatives", "usage", "modelVersion"]
            ):
                self.logger.error("Invalid response structure: %s", response)
                raise AICompletionError("Неверная структура ответа от API")

            return AIResponseSchema(success=True, result=ResultSchema(**result_data))

        except Exception as e:
            self.logger.error("Ошибка при запросе к API Yandex: %s", str(e))
            raise AICompletionError(str(e))
