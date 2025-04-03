from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from .producers import EmailProducer

# Создаем роутер для тестирования отправки email
email_test_router = APIRouter(prefix="/api/test", tags=["Email Testing"])


class TestEmailRequest(BaseModel):
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
