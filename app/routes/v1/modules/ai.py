from typing import Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Body, Depends, Form, Query
from fastapi.responses import StreamingResponse

from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas import (AIChatHistoryClearResponseSchema, AIResponseSchema,
                         AISettingsResponseSchema,
                         AISettingsUpdateResponseSchema,
                         AISettingsUpdateSchema, CurrentUserSchema)
from app.schemas.v1.modules.ai import (AIChatCreateResponseSchema,
                                       AIChatCreateSchema,
                                       AIChatDeleteResponseSchema,
                                       AIChatResponseSchema,
                                       AIChatsListResponseSchema,
                                       AIChatStatsResponseSchema,
                                       AIChatUpdateResponseSchema,
                                       AIChatUpdateSchema)
from app.services.v1.modules.ai.service import AIService


class AIRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="ai", tags=["AI Assistant"])

    def configure(self):

        @self.router.post(path="/completion", response_model=AIResponseSchema)
        @inject
        async def get_ai_completion(
            chat_id: str,
            ai_service: FromDishka[AIService],
            message: str = Form(...),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIResponseSchema:
            """
            # Получение ответа от нейронной сети

            ## Args
            * **chat_id** - ID чата
            * **message** - Текст сообщения пользователя

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
            return await ai_service.get_completion(message, current_user.id, chat_id)

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

        @self.router.put(
            path="/settings", response_model=AISettingsUpdateResponseSchema
        )
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
            update_fields = {
                k: v for k, v in settings_update.model_dump().items() if v is not None
            }
            updated_settings = await ai_service.update_user_ai_settings(
                current_user.id, update_fields
            )
            return AISettingsUpdateResponseSchema(data=updated_settings)

        @self.router.post(
            path="/history/clear", response_model=AIChatHistoryClearResponseSchema
        )
        @inject
        async def clear_chat_history(
            chat_id: str,
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatHistoryClearResponseSchema:
            """
            # Очистка истории чата с AI

            ## Args
            * **chat_id** - ID чата

            ## Returns
            * **AIChatHistoryClearResponseSchema** - Ответ об успешной очистке:
                * **message** - Сообщение о результате операции
                * **success** - Признак успешного выполнения операции
            """
            return await ai_service.clear_chat_history(current_user.id, chat_id)

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
            return await ai_service.export_chat_history_markdown(current_user)

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
            return await ai_service.export_chat_history_text(current_user)

        @self.router.get(path="/chats", response_model=AIChatsListResponseSchema)
        @inject
        async def get_user_chats(
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatsListResponseSchema:
            """
            # Получение списка чатов пользователя

            Возвращает список всех активных чатов текущего пользователя.

            ## Returns
            * **AIChatsListResponseSchema** - Ответ со списком чатов:
                * **message** - Сообщение о результате операции
                * **data** - Список чатов пользователя
            """
            return await ai_service.get_user_chats(current_user.id)

        @self.router.post(path="/chats", response_model=AIChatCreateResponseSchema)
        @inject
        async def create_chat(
            ai_service: FromDishka[AIService],
            chat_data: AIChatCreateSchema = Body(...),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatCreateResponseSchema:
            """
            # Создание нового чата

            Создает новый чат для текущего пользователя.

            ## Args
            * **chat_data** - Данные для создания чата:
                * **title** - Название чата
                * **description** - Описание чата (опционально)

            ## Returns
            * **AIChatCreateResponseSchema** - Ответ с данными созданного чата:
                * **message** - Сообщение о результате операции
                * **data** - Данные созданного чата
            """
            return await ai_service.create_chat(
                user_id=current_user.id,
                title=chat_data.title,
                description=chat_data.description,
            )

        @self.router.get(path="/chats/search", response_model=AIChatsListResponseSchema)
        @inject
        async def search_chats(
            ai_service: FromDishka[AIService],
            q: str = Query(..., description="Поисковый запрос"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatsListResponseSchema:
            """
            # Поиск чатов

            Поиск чатов по названию или описанию.

            ## Args
            * **q** - Поисковый запрос

            ## Returns
            * **AIChatsListResponseSchema** - Ответ со списком найденных чатов:
                * **message** - Сообщение о результате операции
                * **data** - Список найденных чатов
            """
            return await ai_service.search_chats(current_user.id, q)

        @self.router.get(path="/chats/stats", response_model=AIChatStatsResponseSchema)
        @inject
        async def get_chats_stats(
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatStatsResponseSchema:
            """
            # Получение статистики по чатам

            Возвращает расширенную статистику по чатам пользователя, включая информацию
            о расходах на токены и использовании разных моделей.

            ## Returns
            * **AIChatStatsResponseSchema** - Ответ со статистикой:
                * **message** - Сообщение о результате операции
                * **data** - Статистика по чатам:
                    * **total_chats** - Общее количество чатов
                    * **active_chats** - Количество активных чатов
                    * **inactive_chats** - Количество неактивных чатов
                    * **total_messages** - Общее количество сообщений
                    * **total_tokens** - Общее количество токенов
                    * **total_cost** - Общая стоимость использования в рублях
                    * **models_usage** - Статистика использования по моделям
                    * **last_active_chat** - Последний активный чат
            """
            return await ai_service.get_user_chats_stats(current_user.id)

        @self.router.get(path="/chats/{chat_id}", response_model=AIChatResponseSchema)
        @inject
        async def get_chat(
            chat_id: str,
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatResponseSchema:
            """
            # Получение информации о чате

            Возвращает информацию о конкретном чате пользователя.

            ## Args
            * **chat_id** - ID чата, который нужно получить

            ## Returns
            * **AIChatResponseSchema** - Ответ с данными чата:
                * **message** - Сообщение о результате операции
                * **data** - Данные чата
            """
            return await ai_service.get_chat(chat_id, current_user.id)

        @self.router.put(
            path="/chats/{chat_id}", response_model=AIChatUpdateResponseSchema
        )
        @inject
        async def update_chat(
            chat_id: str,
            ai_service: FromDishka[AIService],
            chat_data: AIChatUpdateSchema = Body(...),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatUpdateResponseSchema:
            """
            # Обновление чата

            Обновляет информацию о чате пользователя.

            ## Args
            * **chat_id** - ID чата
            * **chat_data** - Данные для обновления чата:
                * **title** - Новое название чата (опционально)
                * **description** - Новое описание чата (опционально)
                * **is_active** - Новый статус активности (опционально)

            ## Returns
            * **AIChatUpdateResponseSchema** - Ответ с обновленными данными чата:
                * **message** - Сообщение о результате операции
                * **data** - Обновленные данные чата
            """
            # Преобразуем схему в словарь, исключая None значения
            update_fields = {
                k: v for k, v in chat_data.model_dump().items() if v is not None
            }

            return await ai_service.update_chat(chat_id, current_user.id, update_fields)

        @self.router.delete(
            path="/chats/{chat_id}", response_model=AIChatDeleteResponseSchema
        )
        @inject
        async def delete_chat(
            chat_id: str,
            ai_service: FromDishka[AIService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatDeleteResponseSchema:
            """
            # Удаление чата

            Удаляет чат пользователя (мягкое удаление).

            ## Args
            * **chat_id** - ID чата

            ## Returns
            * **AIChatDeleteResponseSchema** - Ответ об успешном удалении:
                * **message** - Сообщение о результате операции
                * **success** - Признак успешного выполнения операции
            """
            return await ai_service.delete_chat(chat_id, current_user.id)

        @self.router.post(
            path="/chats/{chat_id}/duplicate", response_model=AIChatCreateResponseSchema
        )
        @inject
        async def duplicate_chat(
            chat_id: str,
            ai_service: FromDishka[AIService],
            new_title: Optional[str] = Query(
                None, description="Новое название для дубликата чата"
            ),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AIChatCreateResponseSchema:
            """
            # Дублирование чата

            Создает копию существующего чата вместе с историей сообщений.

            ## Args
            * **chat_id** - ID исходного чата
            * **new_title** - Новое название для дубликата (опционально)

            ## Returns
            * **AIChatCreateResponseSchema** - Ответ с данными созданного дубликата:
                * **message** - Сообщение о результате операции
                * **data** - Данные созданного чата
            """
            return await ai_service.duplicate_chat(chat_id, current_user.id, new_title)
