import datetime
from typing import Optional
from io import StringIO
from fastapi.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (AIHistoryNotFoundError, AIConfigError,
                                 AIAuthError, AICompletionError, AIHistoryExportError)
from app.core.integrations.cache.ai import AIRedisStorage
from app.core.integrations.http.ai import AIHttpClient
from app.core.settings import settings
from app.models import ModelType
from app.schemas import (CurrentUserSchema, AIRequestSchema, AIResponseSchema,
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

        Raises:
            AICompletionError: При ошибке получения ответа от AI
            AIConfigError: При ошибке конфигурации AI
            AIAuthError: При ошибке авторизации в API AI
        """
        try:

            # Получаем настройки пользователя из БД
            user_settings = await self.data_manager.get_user_settings(user_id)

            # Получаем историю
            try:
                message_history = await self.storage.get_chat_history(user_id)
            except Exception as e:
                self.logger.error("Ошибка получения истории чата: %s", str(e))
                raise AIHistoryNotFoundError(f"Не удалось получить историю чата: {str(e)}") from e

            # Создаем новое сообщение
            new_message = MessageSchema(role=role, text=message)

            # Добавляем новое сообщение в историю
            message_history.append(new_message)

            # Определяем системное сообщение
            system_message = MessageSchema(
                role=MessageRole.SYSTEM.value,
                # Используем пользовательское системное сообщение, если оно задано
                # иначе используем значение по умолчанию
                text=user_settings.system_message or settings.YANDEX_PRE_INSTRUCTIONS
            )

            # Формируем полный список сообщений
            messages = [system_message] + message_history

            # Если модель не указана, получаем её из настроек пользователя
            if model_type is None:
                model_type = user_settings.preferred_model

            # В зависимости от выбранной модели формируем model_uri
            try:
                model_uri = self.get_model_uri(model_type)
            except Exception as e:
                self.logger.error("Ошибка получения URI модели: %s", str(e))
                raise AIConfigError(f"Не удалось получить URI модели: {str(e)}") from e

            request = AIRequestSchema(
                modelUri=model_uri,
                completionOptions=CompletionOptionsSchema(
                    maxTokens=user_settings.max_tokens,
                    temperature=user_settings.temperature,
                ),
                messages=messages,
            )

            try:
                response = await self.http_client.get_completion(request)
            except Exception as e:
                self.logger.error("Ошибка при запросе к AI API: %s", str(e))
                if "401" in str(e) or "unauthorized" in str(e).lower():
                    raise AIAuthError(f"Ошибка авторизации при запросе к AI API: {str(e)}") from e
                raise AICompletionError(f"Не удалось получить ответ от AI: {str(e)}") from e

            # Добавляем ответ ассистента в историю
            if response.success:
                assistant_message = MessageSchema(
                    role=MessageRole.ASSISTANT,
                    text=response.result.alternatives[0].message.text,
                )
                message_history.append(assistant_message)

                # Сохраняем обновленную историю
                try:
                    await self.storage.save_chat_history(user_id, message_history)
                except Exception as e:
                    self.logger.error("Ошибка сохранения истории чата: %s", str(e))
            else:
                raise AICompletionError("Модель не вернула успешный ответ")
            return response

        except (AICompletionError, AIConfigError, AIAuthError, AIHistoryNotFoundError) as e:
            # Пробрасываем специфические исключения дальше
            raise

        except Exception as e:
            self.logger.error("Непредвиденная ошибка в get_completion: %s", str(e))
            try:
                await self.storage.clear_chat_history(user_id)
            except Exception as clear_error:
                self.logger.error("Ошибка при очистке истории чата: %s", str(clear_error))
            raise AICompletionError(f"Непредвиденная ошибка: {str(e)}") from e

    def get_model_uri(self, model_type: ModelType) -> str:
        """
        Формирует URI модели в зависимости от типа

        Args:
            model_type (ModelType): тип модели

        Returns:
            str: URI модели

        Raises:
            AIConfigError: При ошибке конфигурации или неподдерживаемом типе модели
        """
        try:
            folder_id = settings.YANDEX_FOLDER_ID.get_secret_value()
            if not folder_id:
                raise AIConfigError("Не указан YANDEX_FOLDER_ID в настройках")

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
            if not model_name:
                raise AIConfigError(f"Неподдерживаемый тип модели: {model_type}")

            model_version = settings.YANDEX_MODEL_VERSION
            if not model_version:
                raise AIConfigError("Не указана версия модели в настройках")

            return f"gpt://{folder_id}/{model_name}/{model_version}"

        except Exception as e:
            if isinstance(e, AIConfigError):
                raise
            raise AIConfigError(f"Ошибка при формировании URI модели: {str(e)}") from e

    async def get_user_ai_settings(self, user_id: int) -> AISettingsSchema:
        """
        Получает настройки AI пользователя

        Args:
            user_id: ID пользователя

        Returns:
            AISettingsSchema: Настройки пользователя

        Raises:
            AIConfigError: При ошибке получения настроек пользователя
        """
        try:
            settings = await self.data_manager.get_user_settings(user_id)
            return AISettingsSchema.model_validate(settings)
        except Exception as e:
            self.logger.error("Ошибка получения настроек пользователя: %s", str(e))
            raise AIConfigError(f"Не удалось получить настройки пользователя: {str(e)}") from e

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

        Raises:
            AIConfigError: При ошибке обновления настроек пользователя
        """
        try:
            # Получаем текущие настройки
            current_settings = await self.data_manager.get_user_settings(user_id)

            # Обновляем настройки
            updated_settings = await self.data_manager.update_items(
                current_settings.id,
                settings_data
            )

            return updated_settings
        except Exception as e:
            self.logger.error("Ошибка обновления настроек пользователя: %s", str(e))
            raise AIConfigError(f"Не удалось обновить настройки пользователя: {str(e)}") from e

    async def clear_chat_history(self, user_id: int) -> bool:
        """
        Очищает историю чата пользователя

        Args:
            user_id: ID пользователя

        Returns:
            bool: True, если операция выполнена успешно

        Raises:
            AIHistoryNotFoundError: При ошибке очистки истории чата
        """
        try:
            await self.storage.clear_chat_history(user_id)
            return True
        except Exception as e:
            self.logger.error("Ошибка очистки истории чата: %s", str(e))
            raise AIHistoryNotFoundError(f"Не удалось очистить историю чата: {str(e)}") from e

    async def export_chat_history_markdown(self, user: CurrentUserSchema) -> StreamingResponse:
        """
        Экспортирует историю чата пользователя в формате Markdown

        Args:
            user: Информация о текущем пользователе

        Returns:
            StreamingResponse: Поток с файлом в формате Markdown

        Raises:
            AIHistoryNotFoundError: При отсутствии истории чата
            AIHistoryExportError: При ошибке экспорта истории чата
        """
        try:
            # Получаем историю из хранилища
            try:
                message_history = await self.storage.get_chat_history(user.id)
                if not message_history:
                    raise AIHistoryNotFoundError("История чата пуста")
            except Exception as e:
                if isinstance(e, AIHistoryNotFoundError):
                    raise
                self.logger.error("Ошибка получения истории чата: %s", str(e))
                raise AIHistoryNotFoundError(f"Не удалось получить историю чата: {str(e)}") from e

            # Получаем информацию о пользователе
            user_name = user.username

            # Получаем настройки пользователя для определения модели
            try:
                user_settings = await self.data_manager.get_user_settings(user.id)
                model_type = user_settings.preferred_model
                model_name = self.get_model_display_name(model_type)
            except Exception as e:
                self.logger.error("Ошибка получения настроек пользователя: %s", str(e))
                model_name = "AI Ассистент"

            # Создаем буфер для записи markdown
            markdown_buffer = StringIO()

            # Добавляем заголовок
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            markdown_buffer.write(f"# История чата с AI\n\n")
            markdown_buffer.write(f"Дата экспорта: {current_date}\n")
            markdown_buffer.write(f"Модель: {model_name}\n\n")

            # Добавляем сообщения
            for message in message_history:
                # Определяем префикс в зависимости от роли
                if message.role == MessageRole.USER:
                    prefix = f"## 👤 {user_name}"
                elif message.role == MessageRole.ASSISTANT:
                    prefix = f"## 🤖 {model_name}"
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
        except (AIHistoryNotFoundError, AIHistoryExportError) as e:
            # Пробрасываем специфические исключения дальше
            raise
        except Exception as e:
            self.logger.error("Ошибка экспорта истории в формате markdown: %s", str(e))
            raise AIHistoryExportError(f"Ошибка при экспорте истории чата: {str(e)}") from e

    async def export_chat_history_text(self, user: CurrentUserSchema) -> StreamingResponse:
        """
        Экспортирует историю чата пользователя в текстовом формате

        Args:
            user: Информация о текущем пользователе

        Returns:
            StreamingResponse: Поток с текстовым файлом

        Raises:
            AIHistoryNotFoundError: При отсутствии истории чата
            AIHistoryExportError: При ошибке экспорта истории чата
        """
        try:
            # Получаем историю из хранилища
            try:
                message_history = await self.storage.get_chat_history(user.id)
                if not message_history:
                    raise AIHistoryNotFoundError("История чата пуста")
            except Exception as e:
                if isinstance(e, AIHistoryNotFoundError):
                    raise
                self.logger.error("Ошибка получения истории чата: %s", str(e))
                raise AIHistoryNotFoundError(f"Не удалось получить историю чата: {str(e)}") from e

            # Получаем имя пользователя
            user_name = user.username

            # Получаем настройки пользователя для определения модели
            try:
                user_settings = await self.data_manager.get_user_settings(user.id)
                model_type = user_settings.preferred_model
                model_name = self.get_model_display_name(model_type)
            except Exception as e:
                self.logger.error("Ошибка получения настроек пользователя: %s", str(e))
                model_name = "AI Ассистент"

            # Создаем буфер для записи текста
            text_buffer = StringIO()

            # Добавляем заголовок
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text_buffer.write(f"История чата с AI\n")
            text_buffer.write(f"Дата экспорта: {current_date}\n")
            text_buffer.write(f"Модель: {model_name}\n\n")

            # Добавляем сообщения
            for message in message_history:
                # Определяем префикс в зависимости от роли
                if message.role == MessageRole.USER:
                    prefix = f"{user_name}:"
                elif message.role == MessageRole.ASSISTANT:
                    prefix = f"{model_name}:"
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
        except (AIHistoryNotFoundError, AIHistoryExportError) as e:
            # Пробрасываем специфические исключения дальше
            raise
        except Exception as e:
            self.logger.error("Ошибка экспорта истории в текстовом формате: %s", str(e))
            raise AIHistoryExportError(f"Ошибка при экспорте истории чата: {str(e)}") from e

    def get_model_display_name(self, model_type: ModelType) -> str:
        """
        Возвращает отображаемое имя модели

        Args:
            model_type: Тип модели

        Returns:
            str: Отображаемое имя модели

        Raises:
            AIConfigError: При неизвестном типе модели
        """
        try:
            model_display_names = {
                ModelType.YANDEX_GPT_LITE: "YandexGPT Lite",
                ModelType.YANDEX_GPT_PRO: "YandexGPT Pro",
                ModelType.YANDEX_GPT_PRO_32K: "YandexGPT Pro 32K",
                ModelType.LLAMA_8B: "Llama 8B",
                ModelType.LLAMA_70B: "Llama 70B",
                ModelType.CUSTOM: "Кастомная модель",
            }

            if model_type not in model_display_names:
                self.logger.warning("Неизвестный тип модели: %s", model_type)
                return "AI Ассистент"

            return model_display_names[model_type]
        except Exception as e:
            self.logger.error("Ошибка получения отображаемого имени модели: %s", str(e))
            return "AI Ассистент"