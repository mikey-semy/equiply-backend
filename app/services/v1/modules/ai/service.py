import datetime
from io import StringIO
from typing import Optional

from fastapi.responses import StreamingResponse
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (AIAuthError, AICompletionError, AIConfigError,
                                 AIHistoryExportError, AIHistoryNotFoundError)
from app.core.exceptions.modules.ai import (AIChatDuplicateError,
                                            AIChatNotFoundError)
from app.core.integrations.cache.ai import AIRedisStorage
from app.core.integrations.http.ai import AIHttpClient
from app.core.settings import settings
from app.models import AIChatModel, ModelType
from app.schemas import (AIRequestSchema, AIResponseSchema, AISettingsSchema,
                         CompletionOptionsSchema, CurrentUserSchema,
                         MessageRole, MessageSchema)
from app.schemas.v1.modules.ai import (AIChatCreateResponseSchema,
                                       AIChatDeleteResponseSchema,
                                       AIChatHistoryClearResponseSchema,
                                       AIChatResponseSchema,
                                       AIChatsListResponseSchema,
                                       AIChatStatsResponseSchema,
                                       AIChatUpdateResponseSchema,
                                       ChatStatsDataSchema,
                                       ModelUsageStatsSchema)
from app.services.v1.base import BaseService
from app.services.v1.modules.ai.pricing import ModelPricingCalculator

from .data_manager import AIChatManager, AIDataManager


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
        self.chat_manager = AIChatManager(session)
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
        chat_id: str,
        model_type: Optional[ModelType] = None,
        role: MessageRole = MessageRole.USER,
    ) -> AIResponseSchema:
        """
        Получает ответ от модели на основе истории сообщений

        Args:
            message: Текст сообщения
            user_id: ID пользователя
            chat_id: ID чата
            model_type: Тип модели (опционально)
            role: Роль отправителя сообщения

        Returns:
            AIResponseSchema: Ответ от модели

        Raises:
            AICompletionError: При ошибке получения ответа от AI
            AIConfigError: При ошибке конфигурации AI
            AIAuthError: При ошибке авторизации в API AI
            AIHistoryNotFoundError: При отсутствии истории чата или чат не найден
        """
        try:
            chat = await self.chat_manager.get_model_by_field("chat_id", chat_id)

            if not chat or chat.user_id != user_id:
                raise AIHistoryNotFoundError(f"Чат с ID {chat_id} не найден")

            # Получаем настройки пользователя из БД
            user_settings = await self.data_manager.get_user_settings(user_id)

            # Получаем историю
            try:
                message_history = await self.storage.get_chat_history(user_id, chat_id)
            except Exception as e:
                self.logger.error("Ошибка получения истории чата: %s", str(e))
                raise AIHistoryNotFoundError(
                    f"Не удалось получить историю чата: {str(e)}"
                ) from e

            # Создаем новое сообщение
            new_message = MessageSchema(role=role, text=message)

            # Добавляем новое сообщение в историю
            message_history.append(new_message)

            # Определяем системное сообщение
            system_message = MessageSchema(
                role=MessageRole.SYSTEM.value,
                # Используем пользовательское системное сообщение, если оно задано
                # иначе используем значение по умолчанию
                text=user_settings.system_message or settings.YANDEX_PRE_INSTRUCTIONS,
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
                    raise AIAuthError(
                        f"Ошибка авторизации при запросе к AI API: {str(e)}"
                    ) from e
                raise AICompletionError(
                    f"Не удалось получить ответ от AI: {str(e)}"
                ) from e

            # Добавляем ответ ассистента в историю
            if response.success:
                assistant_message = MessageSchema(
                    role=MessageRole.ASSISTANT,
                    text=response.result.alternatives[0].message.text,
                )
                message_history.append(assistant_message)

                # Сохраняем обновленную историю
                try:
                    await self.storage.save_chat_history(user_id, chat_id, message_history)
                except Exception as e:
                    self.logger.error("Ошибка сохранения истории чата: %s", str(e))
            else:
                raise AICompletionError("Модель не вернула успешный ответ")
            return response

        except (
            AICompletionError,
            AIConfigError,
            AIAuthError,
            AIHistoryNotFoundError,
        ):
            # Пробрасываем специфические исключения дальше
            raise

        except Exception as e:
            self.logger.error("Непредвиденная ошибка в get_completion: %s", str(e))
            try:
                await self.storage.clear_chat_history(user_id, chat_id)
            except Exception as clear_error:
                self.logger.error(
                    "Ошибка при очистке истории чата: %s", str(clear_error)
                )
            raise AICompletionError(f"Непредвиденная ошибка: {str(e)}") from e

    async def clear_chat_history(
        self, user_id: int, chat_id: str
    ) -> AIChatHistoryClearResponseSchema:
        """
        Очищает историю конкретного чата пользователя

        Args:
            user_id: ID пользователя
            chat_id: ID чата

        Returns:
            AIChatHistoryClearResponseSchema: Результат очистки истории
        """
        try:
            # Проверяем существование чата
            chat = await self.chat_manager.get_model_by_field("chat_id", chat_id)

            if not chat or chat.user_id != user_id:
                raise AIHistoryNotFoundError(f"Чат с ID {chat_id} не найден")

            success = await self.storage.clear_chat_history(user_id, chat_id)
            return AIChatHistoryClearResponseSchema(success=success)
        except Exception as e:
            self.logger.error("Ошибка очистки истории чата: %s", str(e))
            raise AIHistoryNotFoundError(
                f"Не удалось очистить историю чата: {str(e)}"
            ) from e

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
            user_settings = await self.data_manager.get_user_settings(user_id)
            return AISettingsSchema.model_validate(user_settings)
        except Exception as e:
            self.logger.error("Ошибка получения настроек пользователя: %s", str(e))
            raise AIConfigError(
                f"Не удалось получить настройки пользователя: {str(e)}"
            ) from e

    async def update_user_ai_settings(
        self, user_id: int, settings_data: dict
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
                current_settings.id, settings_data
            )

            return updated_settings
        except Exception as e:
            self.logger.error("Ошибка обновления настроек пользователя: %s", str(e))
            raise AIConfigError(
                f"Не удалось обновить настройки пользователя: {str(e)}"
            ) from e

    async def export_chat_history_markdown(
        self, user: CurrentUserSchema, chat_id: str
    ) -> StreamingResponse:
        """
        Экспортирует историю чата пользователя в формате Markdown

        Args:
            user: Информация о текущем пользователе
            chat_id: ID чата

        Returns:
            StreamingResponse: Поток с файлом в формате Markdown

        Raises:
            AIHistoryNotFoundError: При отсутствии истории чата
            AIHistoryExportError: При ошибке экспорта истории чата
        """
        try:
            # Проверяем существование чата
            chat = await self.chat_manager.get_model_by_field("chat_id", chat_id)

            if not chat or chat.user_id != user.id:
                raise AIHistoryNotFoundError(f"Чат с ID {chat_id} не найден")

            # Получаем историю из хранилища
            try:
                message_history = await self.storage.get_chat_history(user.id, chat_id)
                if not message_history:
                    raise AIHistoryNotFoundError("История чата пуста")
            except Exception as e:
                if isinstance(e, AIHistoryNotFoundError):
                    raise
                self.logger.error("Ошибка получения истории чата: %s", str(e))
                raise AIHistoryNotFoundError(
                    f"Не удалось получить историю чата: {str(e)}"
                ) from e

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
            markdown_buffer.write("# История чата с AI\n\n")
            markdown_buffer.write(f"Название чата: {chat.title}\n")
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
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )
        except (AIHistoryNotFoundError, AIHistoryExportError):
            # Пробрасываем специфические исключения дальше
            raise
        except Exception as e:
            self.logger.error("Ошибка экспорта истории в формате markdown: %s", str(e))
            raise AIHistoryExportError(
                f"Ошибка при экспорте истории чата: {str(e)}"
            ) from e

    async def export_chat_history_text(
        self, user: CurrentUserSchema, chat_id: str
    ) -> StreamingResponse:
        """
        Экспортирует историю чата пользователя в текстовом формате

        Args:
            user: Информация о текущем пользователе
            chat_id: ID чата

        Returns:
            StreamingResponse: Поток с текстовым файлом

        Raises:
            AIHistoryNotFoundError: При отсутствии истории чата
            AIHistoryExportError: При ошибке экспорта истории чата
        """
        try:
            chat = await self.chat_manager.get_model_by_field("chat_id", chat_id)

            if not chat or chat.user_id != user.id:
                raise AIHistoryNotFoundError(f"Чат с ID {chat_id} не найден")
            # Получаем историю из хранилища
            try:

                message_history = await self.storage.get_chat_history(user.id, chat_id)
                if not message_history:
                    raise AIHistoryNotFoundError("История чата пуста")
            except Exception as e:
                if isinstance(e, AIHistoryNotFoundError):
                    raise
                self.logger.error("Ошибка получения истории чата: %s", str(e))
                raise AIHistoryNotFoundError(
                    f"Не удалось получить историю чата: {str(e)}"
                ) from e

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
            text_buffer.write("История чата с AI\n")
            text_buffer.write(f"Название чата: {chat.title}\n")
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
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )
        except (AIHistoryNotFoundError, AIHistoryExportError):
            # Пробрасываем специфические исключения дальше
            raise
        except Exception as e:
            self.logger.error("Ошибка экспорта истории в текстовом формате: %s", str(e))
            raise AIHistoryExportError(
                f"Ошибка при экспорте истории чата: {str(e)}"
            ) from e

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

    async def create_chat(
        self, user_id: int, title: str, description: Optional[str] = None
    ) -> AIChatCreateResponseSchema:
        """
        Создает новый чат для пользователя.

        Args:
            user_id: ID пользователя
            title: Название чата
            description: Описание чата

        Returns:
            AIChatCreateResponseSchema: Результат создания чата
        """
        try:
            chat = await self.chat_manager.create_chat(user_id, title, description)
            return AIChatCreateResponseSchema(data=chat)
        except Exception as e:
            self.logger.error("Ошибка при создании чата: %s", str(e))
            raise AIConfigError(f"Не удалось создать чат: {str(e)}") from e

    async def get_user_chats(self, user_id: int) -> AIChatsListResponseSchema:
        """
        Получает список чатов пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            AIChatsListResponseSchema: Список чатов
        """
        try:
            chats = await self.chat_manager.get_user_chats(user_id)
            return AIChatsListResponseSchema(data=chats)
        except Exception as e:
            self.logger.error("Ошибка при получении списка чатов: %s", str(e))
            raise AIChatNotFoundError(f"Не удалось получить список чатов: {str(e)}") from e

    async def get_chat(self, chat_id: str, user_id: int) -> AIChatResponseSchema:
        """
        Получает чат по ID.

        Args:
            chat_id: ID чата
            user_id: ID пользователя для проверки доступа

        Returns:
            AIChatResponseSchema: Схема чата
        """
        try:
            chat = await self.chat_manager.get_chat(chat_id, user_id)
            return AIChatResponseSchema(data=chat)
        except Exception as e:
            self.logger.error("Ошибка при получении чата: %s", str(e))
            raise AIChatNotFoundError(f"Чат с ID {chat_id} не найден") from e

    async def update_chat(
        self, chat_id: str, user_id: int, update_data: dict
    ) -> AIChatUpdateResponseSchema:
        """
        Обновляет чат.

        Args:
            chat_id: ID чата
            user_id: ID пользователя для проверки доступа
            update_data: Данные для обновления

        Returns:
            AIChatUpdateResponseSchema: Результат обновления чата
        """
        try:
            chat = await self.chat_manager.get_model_by_field("chat_id", chat_id)

            if not chat or chat.user_id != user_id:
                self.logger.warning("Чат с ID %s не найден или доступ запрещен", chat_id)
                raise AIChatNotFoundError(f"Чат с ID {chat_id} не найден")

            updated_chat = await self.chat_manager.update_items(chat.id, update_data)
            return AIChatUpdateResponseSchema(data=updated_chat)
        except Exception as e:
            self.logger.error("Ошибка при обновлении чата: %s", str(e))
            raise AIChatNotFoundError(f"Чат с ID {chat_id} не найден") from e

    async def delete_chat(
        self, chat_id: str, user_id: int
    ) -> AIChatDeleteResponseSchema:
        """
        Удаляет чат (мягкое удаление).

        Args:
            chat_id: ID чата
            user_id: ID пользователя для проверки доступа

        Returns:
            AIChatDeleteResponseSchema: Результат удаления чата
        """
        try:
            chat = await self.chat_manager.get_model_by_field("chat_id", chat_id)

            if not chat or chat.user_id != user_id:
                self.logger.warning("Чат с ID %s не найден или доступ запрещен", chat_id)
                raise AIChatNotFoundError(f"Чат с ID {chat_id} не найден")

            # Мягкое удаление - просто помечаем как неактивный
            await self.chat_manager.update_items(chat.id, {"is_active": False})

            # Также очищаем историю в Redis
            await self.storage.clear_chat_history(user_id, chat_id)

            return True
        except Exception as e:
            self.logger.error("Ошибка при удалении чата: %s", str(e))
            raise AIChatNotFoundError(f"Чат с ID {chat_id} не найден") from e

    async def duplicate_chat(
        self, chat_id: str, user_id: int, new_title: Optional[str] = None
    ) -> AIChatCreateResponseSchema:
        """
        Создает дубликат существующего чата с копированием истории сообщений.

        Args:
            chat_id: ID исходного чата
            user_id: ID пользователя
            new_title: Новое название для дубликата (если None, будет добавлено "(копия)")

        Returns:
            Optional[AIChatSchema]: Созданный дубликат чата или None при ошибке
        """
        try:
            # Проверяем существование исходного чата
            original_chat = await self.chat_manager.get_model_by_field(
                "chat_id", chat_id
            )

            if not original_chat or original_chat.user_id != user_id:
                raise AIChatNotFoundError(f"Чат с ID {chat_id} не найден")

            # Получаем историю исходного чата
            original_history = await self.storage.get_chat_history(user_id, chat_id)

            # Создаем новый чат
            if new_title is None:
                new_title = f"{original_chat.title} (копия)"

            new_chat = await self.chat_manager.create_chat(
                user_id=user_id, title=new_title, description=original_chat.description
            )

            # Копируем историю в новый чат
            if original_history:
                await self.storage.save_chat_history(
                    user_id, new_chat.chat_id, original_history
                )

            return AIChatCreateResponseSchema(
                message="Чат успешно дублирован", data=new_chat
            )
        except Exception as e:
            self.logger.error("Ошибка при дублировании чата: %s", str(e))
            raise AIChatDuplicateError(f"Не удалось дублировать чат с ID {chat_id}") from e

    async def search_chats(self, user_id: int, query: str) -> AIChatsListResponseSchema:
        """
        Поиск чатов по названию или описанию.

        Args:
            user_id: ID пользователя
            query: Поисковый запрос

        Returns:
            AIChatsListResponseSchema: Список найденных чатов
        """
        try:
            # Создаем условия поиска
            statement = (
                select(AIChatModel)
                .where(
                    and_(
                        AIChatModel.user_id == user_id,
                        AIChatModel.is_active ==True,
                        or_(
                            AIChatModel.title.ilike(f"%{query}%"),
                            AIChatModel.description.ilike(f"%{query}%"),
                        ),
                    )
                )
                .order_by(desc(AIChatModel.last_message_at))
            )

            chats = await self.chat_manager.get_items(statement)
            return AIChatsListResponseSchema(
                message=f"Найдено чатов: {len(chats)}", data=chats
            )
        except Exception as e:
            self.logger.error("Ошибка при поиске чатов: %s", str(e))
            raise AIChatNotFoundError(f"Не удалось найти чаты по запросу: {query}") from e

    async def get_user_chats_stats(self, user_id: int) -> AIChatStatsResponseSchema:
        """
        Получает расширенную статистику по чатам пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            AIChatStatsResponseSchema: Статистика по чатам
        """
        try:
            # Получаем все чаты пользователя
            all_chats = await self.chat_manager.get_user_chats(user_id)

            if not all_chats:
                return AIChatStatsResponseSchema(
                    message="Нет доступных чатов для статистики", data=None
                )

            self.logger.debug("Все чаты пользователя: %s", all_chats)

            # Базовая статистика
            total_chats = len(all_chats)
            active_chats = sum(1 for chat in all_chats if chat.is_active)

            # Получаем последний активный чат
            last_active_chat = None
            if all_chats:
                last_active_chat = all_chats[
                    0
                ]  # Чаты уже отсортированы по last_message_at

            # Статистика по использованию моделей
            models_usage = {}
            total_messages = 0
            total_tokens = 0
            total_cost = 0.0

            # Получаем настройки пользователя для определения предпочитаемой модели
            user_settings = await self.data_manager.get_user_settings(user_id)
            preferred_model = user_settings.preferred_model

            # Для каждого чата получаем историю и анализируем использование
            for chat in all_chats:
                try:
                    # Получаем историю чата
                    self.logger.debug("Получаем историю для чата %s", chat.chat_id)
                    messages = await self.storage.get_chat_history(
                        user_id, chat.chat_id
                    )
                    self.logger.debug("Получено сообщений: %d", len(messages))
                    # Считаем сообщения
                    total_messages += len(messages)

                    # Анализируем сообщения от ассистента для подсчета токенов
                    for i in range(
                        1, len(messages), 2
                    ):  # Берем только ответы ассистента
                        if (
                            i < len(messages)
                            and messages[i].role == MessageRole.ASSISTANT
                        ):
                            # Получаем информацию о предыдущем запросе пользователя
                            user_message = messages[i - 1] if i > 0 else None

                            # Примерно оцениваем количество токенов (можно заменить на более точный расчет)
                            input_tokens = (
                                len(user_message.text.split()) * 1.3
                                if user_message
                                else 0
                            )
                            completion_tokens = len(messages[i].text.split()) * 1.3
                            message_tokens = int(input_tokens + completion_tokens)

                            # Добавляем к общей статистике
                            total_tokens += message_tokens

                            # Рассчитываем стоимость
                            message_cost = ModelPricingCalculator.calculate_cost(
                                preferred_model, message_tokens
                            )
                            total_cost += message_cost

                            # Обновляем статистику по модели
                            model_name = ModelPricingCalculator.get_model_display_name(
                                preferred_model
                            )
                            if model_name not in models_usage:
                                models_usage[model_name] = {
                                    "total_tokens": 0,
                                    "total_cost": 0.0,
                                    "usage_count": 0,
                                    "average_tokens": 0.0,
                                }

                            models_usage[model_name]["total_tokens"] += message_tokens
                            models_usage[model_name]["total_cost"] += message_cost
                            models_usage[model_name]["usage_count"] += 1

                except Exception as e:
                    self.logger.warning(
                        "Не удалось получить статистику для чата %s: %s",
                        chat.chat_id,
                        str(e)
                    )
                    continue

            # Рассчитываем средние значения для каждой модели
            for model_name, stats in models_usage.items():
                if stats["usage_count"] > 0:
                    stats["average_tokens"] = (
                        stats["total_tokens"] / stats["usage_count"]
                    )

            # Формируем модели для ответа
            models_usage_schemas = {}
            for model_name, stats in models_usage.items():
                models_usage_schemas[model_name] = ModelUsageStatsSchema(
                    total_tokens=stats["total_tokens"],
                    total_cost=round(stats["total_cost"], 2),
                    usage_count=stats["usage_count"],
                    average_tokens=round(stats["average_tokens"], 1),
                )

            # Создаем данные статистики
            stats_data = ChatStatsDataSchema(
                total_chats=total_chats,
                active_chats=active_chats,
                inactive_chats=total_chats - active_chats,
                total_messages=total_messages,
                total_tokens=total_tokens,
                total_cost=round(total_cost, 2),
                models_usage=models_usage_schemas,
                last_active_chat=last_active_chat,
            )

            return AIChatStatsResponseSchema(
                message="Статистика успешно получена", data=stats_data
            )

        except Exception as e:
            self.logger.error("Ошибка при получении статистики по чатам: %s", str(e))
            raise AIChatNotFoundError(
                f"Не удалось получить статистику по чатам: {str(e)}"
            ) from e
