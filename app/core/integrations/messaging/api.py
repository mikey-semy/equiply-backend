"""
Модуль API endpoints для тестирования системы отправки email.

Предоставляет REST API интерфейс для тестирования функциональности
отправки email через систему очередей FastStream + RabbitMQ.

Endpoints:
- POST /api/test/send-email: Отправка тестового email

Модуль предназначен для:
- Тестирования работы системы сообщений
- Отладки email функциональности
- Демонстрации использования EmailProducer

Использование:
    curl -X POST "http://localhost:8000/api/test/send-email" \
         -H "Content-Type: application/json" \
         -d '{"to_email": "test@example.com", "subject": "Test", "body": "Hello"}'
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from .producers import EmailProducer

# Создаем роутер для тестирования отправки email
email_test_router = APIRouter(prefix="/api/test", tags=["Email Testing"])


class TestEmailRequest(BaseModel):
    """
    Отправляет тестовое письмо через систему очередей FastStream.

    Создает задачу на отправку email и помещает её в очередь RabbitMQ
    для асинхронной обработки consumer'ом.

    Args:
        request (TestEmailRequest): Данные для отправки email
            - to_email: Email получателя
            - subject: Тема письма
            - body: HTML содержимое письма

    Returns:
        Dict[str, Any]: Результат операции
            - status: "success" при успехе
            - message: Сообщение о результате

    Raises:
        HTTPException: При ошибке отправки в очередь
            - status_code: 500
            - detail: Описание ошибки

    Example:
        >>> response = await send_test_email(TestEmailRequest(
        ...     to_email="user@example.com",
        ...     subject="Тест",
        ...     body="<h1>Тестовое письмо</h1>"
        ... ))
        >>> print(response)
        {"status": "success", "message": "Письмо отправлено на user@example.com"}
    """
    to_email: EmailStr
    subject: str = "Тестовое письмо"
    body: str = "<h1>Это тестовое письмо</h1><p>Отправлено через FastStream</p>"


@email_test_router.post("/send-email", summary="Отправить тестовое письмо")
async def send_test_email(request: TestEmailRequest):
    """
    Отправляет тестовое письмо через FastStream
    """
    producer = EmailProducer()

    try:
        await producer.send_email_task(
            to_email=request.to_email, subject=request.subject, body=request.body
        )
        return {
            "status": "success",
            "message": f"Письмо отправлено на {request.to_email}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при отправке письма: {str(e)}"
        )
