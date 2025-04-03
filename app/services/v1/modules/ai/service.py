from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.integrations.cache.ai import AIRedisStorage
from app.core.integrations.http.ai import AIHttpClient
from app.core.settings import settings
from app.models import ModelType
from app.schemas import (AIRequestSchema, AIResponseSchema,
                         CompletionOptionsSchema, MessageRole, MessageSchema)
from app.services.v1.base import BaseService

from .data_manager import AIDataManager


class AIService(BaseService):
    """
    Сервис для работы с чатом с AI

    Attributes:
        session: Сессия базы данных
        http_client: HTTP клиент для работы с AI API
    """

    def __init__(
        self,
        session: AsyncSession,
        storage: AIRedisStorage,
    ):
        super().__init__(session)
        self.data_manager = AIDataManager(session)
        self.storage = storage
        self.http_client = AIHttpClient()
        self.max_tokens = settings.YANDEX_MAX_TOKENS

    SYSTEM_MESSAGE = MessageSchema(
        role=MessageRole.SYSTEM.value, text=settings.YANDEX_PRE_INSTRUCTIONS
    )

    async def get_completion(
        self,
        message: str,
        user_id: int,
        model_type: Optional[ModelType] = None,
        role: MessageRole = MessageRole.USER,
    ) -> AIResponseSchema:
        """
        Получает ответ от модели на основе истории сообщений

        Args:
            request: Запрос к AI модели

        Returns:
            AIResponseSchema: Ответ от модели
        """
        try:

            # Получаем настройки пользователя из БД
            user_settings = await self.data_manager.get_user_settings(user_id)

            # Получаем историю
            message_history = await self.storage.get_chat_history(user_id)

            # Создаем новое сообщение
            new_message = MessageSchema(role=role, text=message)

            # Добавляем новое сообщение в историю
            message_history.append(new_message)

            # Формируем полный список сообщений
            messages = [self.SYSTEM_MESSAGE] + message_history

            # Если модель не указана, получаем её из настроек пользователя
            if model_type is None:
                model_type = user_settings.preferred_model

            # В зависимости от выбранной модели формируем model_uri
            model_uri = self.get_model_uri(model_type)

            request = AIRequestSchema(
                modelUri=model_uri,
                completionOptions=CompletionOptionsSchema(
                    maxTokens=user_settings.max_tokens,
                    temperature=user_settings.temperature,
                ),
                messages=messages,
            )

            response = await self.http_client.get_completion(request)

            # Добавляем ответ ассистента в историю
            if response.success:
                assistant_message = MessageSchema(
                    role=MessageRole.ASSISTANT,
                    text=response.result.alternatives[0].message.text,
                )
                message_history.append(assistant_message)

                # Сохраняем обновленную историю
                await self.storage.save_chat_history(user_id, message_history)

            return response
        except Exception as e:
            self.logger.error("Error in get_completion: %s", str(e))
            await self.storage.clear_chat_history(user_id)
            raise

    def get_model_uri(self, model_type: ModelType) -> str:
        """Формирует URI модели в зависимости от типа"""
        folder_id = settings.YANDEX_FOLDER_ID.get_secret_value()

        # Маппинг типов моделей на имена моделей
        model_mapping = {
            ModelType.YANDEX_GPT_LITE: "yandexgpt-lite",
            ModelType.YANDEX_GPT_PRO: "yandexgpt",
            ModelType.YANDEX_GPT_PRO_32K: "yandexgpt-32k",
            ModelType.LLAMA_8B: "llama-lite",
            ModelType.LLAMA_70B: "llama",
            ModelType.CUSTOM: "custom",  # Для кастомной модели нужна отдельная  логика
        }

        model_name = model_mapping.get(model_type, "llama")  # По умолчанию llama
        model_version = settings.YANDEX_MODEL_VERSION

        return f"gpt://{folder_id}/{model_name}/{model_version}"
