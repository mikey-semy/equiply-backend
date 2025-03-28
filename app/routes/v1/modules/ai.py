from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Form

from app.core.security.auth import get_current_user
from app.models import ModelType
from app.routes.base import BaseRouter
from app.schemas import AIResponseSchema, CurrentUserSchema
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
