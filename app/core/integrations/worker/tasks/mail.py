import asyncio
from app.core.integrations.worker.base import celery_app
from app.core.integrations.mail.base import BaseEmailDataManager


@celery_app.task
def send_email(to_email: str, subject: str, body: str):
    """
    Отправка email через Celery

    Args:
        to_email (str): Email адрес получателя
        subject (str): Тема письма
        body (str): HTML-содержимое письма

    Returns:
        dict: Статус отправки письма
    """
    email_manager = BaseEmailDataManager()
    # Проверяем, является ли метод асинхронным
    if asyncio.iscoroutinefunction(email_manager.send_email):
        # Запускаем асинхронный метод в синхронном контексте
        loop = asyncio.get_event_loop()
        loop.run_until_complete(email_manager.send_email(to_email=to_email, subject=subject, body=body))
    else:
        # Если метод синхронный, вызываем его напрямую
        email_manager.send_email(to_email=to_email, subject=subject, body=body)
    return {"status": "sent", "to": to_email, "subject": subject}

@celery_app.task
def send_registration_success_email(user_id: int, email: str, user_name: str):
    """
    Отправка письма об успешной регистрации

    Args:
        user_id (int): ID пользователя
        email (str): Email адрес получателя
        user_name (str): Имя пользователя для персонализации письма

    Returns:
        dict: Статус отправки письма
    """
    from app.core.integrations.mail.auth import AuthEmailDataManager
    email_manager = AuthEmailDataManager()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        email_manager.send_registration_success_email(to_email=email, user_name=user_name)
    )
    return {"status": "sent", "to": email, "type": "registration_success"}

@celery_app.task
def send_verification_email(user_id: int, email: str, user_name: str, token: str):
    """
    Отправка письма для подтверждения email

    Args:
        user_id (int): ID пользователя
        email (str): Email адрес получателя
        user_name (str): Имя пользователя для персонализации письма
        token (str): Токен для подтверждения email

    Returns:
        dict: Статус отправки письма
    """
    from app.core.integrations.mail.auth import AuthEmailDataManager
    email_manager = AuthEmailDataManager()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        email_manager.send_verification_email(
            to_email=email, user_name=user_name, verification_token=token
        )
    )
    return {"status": "sent", "to": email, "type": "verification"}

@celery_app.task
def send_password_reset_email(user_id: int, email: str, user_name: str, token: str):
    """
    Отправка письма для сброса пароля

    Args:
        user_id (int): ID пользователя
        email (str): Email адрес получателя
        user_name (str): Имя пользователя для персонализации письма
        token (str): Токен для сброса пароля

    Returns:
        dict: Статус отправки письма
    """
    from app.core.integrations.mail.auth import AuthEmailDataManager
    email_manager = AuthEmailDataManager()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        email_manager.send_password_reset_email(
            to_email=email, user_name=user_name, reset_token=token
        )
    )
    return {"status": "sent", "to": email, "type": "password_reset"}
