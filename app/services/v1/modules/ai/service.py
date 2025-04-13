import datetime
from typing import Optional

from fastapi.responses import StreamingResponse
from io import StringIO
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.integrations.cache.ai import AIRedisStorage
from app.core.integrations.http.ai import AIHttpClient
from app.core.settings import settings
from app.models import ModelType
from app.schemas import (AIRequestSchema, AIResponseSchema,
                         CompletionOptionsSchema, MessageRole, MessageSchema,
                         AISettingsSchema)
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

    async def get_user_ai_settings(self, user_id: int) -> AISettingsSchema:
        """
        Получает настройки AI пользователя

        Args:
            user_id: ID пользователя

        Returns:
            AISettingsSchema: Настройки пользователя
        """
        settings = await self.data_manager.get_user_settings(user_id)
        return AISettingsSchema.model_validate(settings)

    async def update_user_ai_settings(
        self,
        user_id: int,
        settings_data: dict
    ) -> AISettingsSchema:
        """
        Обновляет настройки AI пользователя

        Args:
            user_id: ID пользователя
            settings_data: Данные для обновления настроек

        Returns:
            AISettingsSchema: Обновленные настройки пользователя
        """
        # Получаем текущие настройки
        current_settings = await self.data_manager.get_user_settings(user_id)

        # Обновляем настройки
        updated_settings = await self.data_manager.update_items(
            current_settings.id,
            settings_data
        )

        return updated_settings

    async def clear_chat_history(self, user_id: int) -> bool:
        """
        Очищает историю чата пользователя

        Args:
            user_id: ID пользователя

        Returns:
            bool: True, если операция выполнена успешно
        """
        await self.storage.clear_chat_history(user_id)
        return True

    async def export_chat_history_markdown(self, user_id: int) -> StreamingResponse:
        """
        Экспортирует историю чата пользователя в формате Markdown

        Args:
            user_id: ID пользователя

        Returns:
            StreamingResponse: Поток с файлом в формате Markdown
        """
        try:
            # Получаем историю из хранилища
            message_history = await self.storage.get_chat_history(user_id)

            # Создаем буфер для записи markdown
            markdown_buffer = StringIO()

            # Добавляем заголовок
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            markdown_buffer.write(f"# История чата с AI\n\n")
            markdown_buffer.write(f"Дата экспорта: {current_date}\n\n")

            # Добавляем сообщения
            for message in message_history:
                # Определяем префикс в зависимости от роли
                if message.role == MessageRole.USER:
                    prefix = "## 👤 Пользователь"
                elif message.role == MessageRole.ASSISTANT:
                    prefix = "## 🤖 Ассистент"
                else:
                    prefix = f"## {message.role.capitalize()}"

                # Записываем сообщение
                markdown_buffer.write(f"{prefix}\n\n{message.text}\n\n")

            # Перемещаем указатель в начало буфера
            markdown_buffer.seek(0)

            # Создаем имя файла с текущей датой
            filename = f"ai_chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            # Возвращаем поток с файлом
            return StreamingResponse(
                markdown_buffer,
                media_type="text/markdown",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        except Exception as e:
            self.logger.error("Error exporting chat history to markdown: %s", str(e))
            # В случае ошибки возвращаем пустой файл с сообщением об ошибке
            error_buffer = StringIO("# Ошибка при экспорте истории чата\n\nК сожалению, произошла ошибка при экспорте истории чата.")
            error_buffer.seek(0)
            return StreamingResponse(
                error_buffer,
                media_type="text/markdown",
                headers={"Content-Disposition": f"attachment; filename=error_export.md"}
            )

    async def export_chat_history_text(self, user_id: int) -> StreamingResponse:
        """
        Экспортирует историю чата пользователя в текстовом формате

        Args:
            user_id: ID пользователя

        Returns:
            StreamingResponse: Поток с текстовым файлом
        """
        try:
            # Получаем историю из хранилища
            message_history = await self.storage.get_chat_history(user_id)

            # Создаем буфер для записи текста
            text_buffer = StringIO()

            # Добавляем заголовок
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text_buffer.write(f"История чата с AI\n")
            text_buffer.write(f"Дата экспорта: {current_date}\n\n")

            # Добавляем сообщения
            for message in message_history:
                # Определяем префикс в зависимости от роли
                if message.role == MessageRole.USER:
                    prefix = "Пользователь:"
                elif message.role == MessageRole.ASSISTANT:
                    prefix = "Ассистент:"
                else:
                    prefix = f"{message.role.capitalize()}:"

                # Записываем сообщение
                text_buffer.write(f"{prefix}\n{message.text}\n\n")

            # Перемещаем указатель в начало буфера
            text_buffer.seek(0)

            # Создаем имя файла с текущей датой
            filename = f"ai_chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            # Возвращаем поток с файлом
            return StreamingResponse(
                text_buffer,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        except Exception as e:
            self.logger.error("Error exporting chat history to text: %s", str(e))
            # В случае ошибки возвращаем пустой файл с сообщением об ошибке
            error_buffer = StringIO("Ошибка при экспорте истории чата\n\nК сожалению, произошла ошибка при экспорте истории чата.")
            error_buffer.seek(0)
            return StreamingResponse(
                error_buffer,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename=error_export.txt"}
            )