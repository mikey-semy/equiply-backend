from typing import Dict, Any, Optional
from .base import ErrorResponseSchema, ErrorSchema

class RateLimitErrorSchema(ErrorSchema):
    """
    Схема для представления данных об ошибке превышения лимита запросов.

    Attributes:
        detail: Подробное описание ошибки
        error_type: Тип ошибки (rate_limit_exceeded)
        status_code: HTTP код ответа (429)
        timestamp: Временная метка возникновения ошибки
        request_id: Уникальный идентификатор запроса
        reset_time: Время в секундах до сброса ограничения
    """
    reset_time: Optional[int] = None

class RateLimitExceededResponseSchema(ErrorResponseSchema):
    """
    Схема ответа при превышении лимита запросов.

    Attributes:
        success: Всегда False для ошибок
        message: Информационное сообщение, обычно None для ошибок
        data: Всегда None для ошибок
        error: Детальная информация об ошибке превышения лимита
    """
    error: RateLimitErrorSchema