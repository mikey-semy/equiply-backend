from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Form, Body
from fastapi.responses import StreamingResponse
from app.core.security.auth import get_current_user
from app.models import ModelType
from app.routes.base import BaseRouter
from app.schemas import (AIResponseSchema, CurrentUserSchema,
AIChatHistoryClearResponseSchema, AIChatHistoryExportResponseSchema,
AISettingsUpdateResponseSchema, AISettingsResponseSchema, AISettingsUpdateSchema)

from app.services.v1.modules.ai.service import AIService


class AIRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="ai", tags=["AI Assistant"])

    def configure(self):

        @self.router.post(path="/completion", response_model=AIResponseSchema)
        @inject
        async def get_ai_completion(
            ai_service: FromDishka[AIService],
            model_type: ModelType = Form(None),
            message: str = Form(...),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIResponseSchema:
            """
            # Получение ответа от нейронной сети

            ## Args
            * **model_type** - Тип модели
            * **message** - Текст сообщения пользователя
            * **db_session** - Сессия базы данных

            ## Returns
            * **AIResponseSchema** - Ответ от модели:
                * **success** - Признак успеха
                * **result** - Результат генерации:
                    * **alternatives** - Варианты ответа
                    * **usage** - Статистика использования токенов
                    * **modelVersion** - Версия модели

            ## Пример ответа
            ```json
            {
                "success": true,
                "result": {
                    "alternatives": [{
                        "message": {
                            "role": "assistant",
                            "text": "Ответ на ваш вопрос..."
                        },
                        "status": "ALTERNATIVE_STATUS_FINAL"
                    }],
                    "usage": {
                        "inputTextTokens": "19",
                        "completionTokens": "6",
                        "totalTokens": "25"
                    },
                    "modelVersion": "23.10.2024"
                }
            }
            ```
            """
            return await ai_service.get_completion(message, current_user.id, model_type)

        @self.router.get(path="/settings", response_model=AISettingsResponseSchema)
        @inject
        async def get_ai_settings(
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AISettingsResponseSchema:
            """
            # Получение текущих настроек AI для пользователя

            ## Returns
            * **AISettingsResponseSchema** - Ответ с настройками пользователя:
                * **message** - Сообщение о результате операции
                * **data** - Данные настроек:
                    * **user_id** - ID пользователя
                    * **preferred_model** - Предпочитаемая модель
                    * **temperature** - Температура генерации
                    * **max_tokens** - Максимальное количество токенов
            """
            settings = await ai_service.get_user_ai_settings(current_user.id)
            return AISettingsResponseSchema(data=settings)

        @self.router.put(path="/settings", response_model=AISettingsUpdateResponseSchema)
        @inject
        async def update_ai_settings(
            ai_service: FromDishka[AIService],
            settings_update: AISettingsUpdateSchema = Body(...),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AISettingsUpdateResponseSchema:
            """
            # Обновление настроек AI для пользователя

            ## Args
            * **settings_update** - Данные для обновления настроек:
                * **preferred_model** - Предпочитаемая модель
                * **temperature** - Температура генерации (от 0 до 1)
                * **max_tokens** - Максимальное количество токенов

            ## Returns
            * **AISettingsUpdateResponseSchema** - Ответ с обновленными настройками:
                * **message** - Сообщение о результате операции
                * **data** - Обновленные данные настроек
            """
            # Преобразуем схему в словарь, исключая None значения
            update_fields = {k: v for k, v in settings_update.model_dump().items() if v is not None}
            updated_settings = await ai_service.update_user_ai_settings(current_user.id, update_fields)
            return AISettingsUpdateResponseSchema(data=updated_settings)

        @self.router.post(
            path="/history/clear",
            response_model=AIChatHistoryClearResponseSchema)
        @inject
        async def clear_chat_history(
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatHistoryClearResponseSchema:
            """
            # Очистка истории чата с AI

            ## Returns
            * **AIChatHistoryClearResponseSchema** - Ответ об успешной очистке:
                * **message** - Сообщение о результате операции
                * **success** - Признак успешного выполнения операции
            """
            success = await ai_service.clear_chat_history(current_user.id)
            return AIChatHistoryClearResponseSchema(success=success)

        @self.router.get(path="/history/export/markdown")
        @inject
        async def export_chat_history_markdown(
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> StreamingResponse:
            """
            # Экспорт истории чата с AI в формате Markdown

            Возвращает файл в формате Markdown (.md) с историей чата.

            ## Returns
            * **StreamingResponse** - Поток с файлом в формате Markdown
            """
            return await ai_service.export_chat_history_markdown(current_user.id)

        @self.router.get(path="/history/export/text")
        @inject
        async def export_chat_history_text(
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> StreamingResponse:
            """
            # Экспорт истории чата с AI в текстовом формате

            Возвращает текстовый файл (.txt) с историей чата.

            ## Returns
            * **StreamingResponse** - Поток с текстовым файлом
            """
            return await ai_service.export_chat_history_text(current_user.id)