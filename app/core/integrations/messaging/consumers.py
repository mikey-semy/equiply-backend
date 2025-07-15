"""
Модуль потребителей сообщений для обработки email задач.

Содержит обработчики (consumers) для различных типов email сообщений,
которые слушают соответствующие очереди RabbitMQ и обрабатывают
поступающие задачи.

Обработчики:
- process_email: Обычные email сообщения
- process_verification_email: Письма верификации
- process_password_reset_email: Письма сброса пароля
- process_registration_success_email: Письма об успешной регистрации

Все обработчики:
- Используют Jinja2 для рендеринга HTML шаблонов
- Логируют результаты с эмодзи для удобства мониторинга
- Возвращают статус выполнения задачи
- Обрабатывают ошибки и логируют их

Зависимости:
- BaseEmailDataManager: Для отправки email
- Jinja2: Для рендеринга HTML шаблонов
- FastStream Logger: Для логирования
"""
import logging

from faststream.rabbit.fastapi import Logger

from app.core.integrations.mail.base import BaseEmailDataManager
from app.schemas import (EmailMessageSchema, PasswordResetEmailSchema,
                         RegistrationSuccessEmailSchema,
                         VerificationEmailSchema)

from .broker import rabbit_router

logger = logging.getLogger("app.email.tasks")
logger.info("✨ Модуль consumers.py загружен")
email_manager = BaseEmailDataManager()


@rabbit_router.subscriber("email_queue")
async def process_email(message: EmailMessageSchema, logger: Logger):
    """
    Обрабатывает задачу отправки обычного email сообщения.

    Этот обработчик слушает очередь "email_queue" и обрабатывает
    обычные email сообщения с готовым содержимым.

    Args:
        message (EmailMessageSchema): Сообщение с данными для отправки email
            - to_email: Email адрес получателя
            - subject: Тема письма
            - body: Готовое содержимое письма (HTML или текст)
        logger (Logger): FastStream логгер для записи информации

    Returns:
        Dict[str, Any]: Результат обработки
            - status: "success" или "error"
            - to_email: Email получателя
            - error: Описание ошибки (при наличии)

    Raises:
        Exception: Обрабатывается внутри функции, не пробрасывается
    """
    logger.info("📨 Обработка email для: %s", message.to_email)

    try:
        await email_manager.send_email(
            to_email=message.to_email, subject=message.subject, body=message.body
        )
        logger.info("✅ Email успешно отправлен: %s", message.to_email)
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error("❌ Ошибка при отправке email: %s", str(e))
        return {"status": "error", "error": str(e), "to_email": message.to_email}


@rabbit_router.subscriber("verification_email_queue")
async def process_verification_email(message: VerificationEmailSchema, logger: Logger):
    """
    Обрабатывает задачу отправки email для верификации.

    Генерирует HTML содержимое на основе шаблона verification.html
    и отправляет письмо с ссылкой для подтверждения email адреса.

    Args:
        message (VerificationEmailSchema): Сообщение с данными для верификации
            - to_email: Email адрес получателя
            - subject: Тема письма
            - verification_token: Токен для генерации ссылки верификации
            - user_name: Имя пользователя (опционально)
        logger (Logger): FastStream логгер для записи информации

    Returns:
        Dict[str, Any]: Результат обработки
            - status: "success" или "error"
            - to_email: Email получателя
            - error: Описание ошибки (при наличии)

    Template variables:
        - user_name: Имя пользователя
        - verification_url: Полная ссылка для верификации

    Raises:
        Exception: Обрабатывается внутри функции, не пробрасывается
    """
    from jinja2 import Environment, FileSystemLoader

    from app.core.settings import settings

    logger.info("📨 Подготовка письма верификации для: %s", message.to_email)

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("verification.html")
        verification_url = f"{settings.VERIFICATION_URL}{message.verification_token}"

        html_content = template.render(
            user_name=message.user_name, verification_url=verification_url
        )

        await email_manager.send_email(
            to_email=message.to_email, subject=message.subject, body=html_content
        )

        logger.info("✅ Письмо верификации отправлено: %s", message.to_email)
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error("❌ Ошибка при отправке письма верификации: %s", str(e))
        return {"status": "error", "error": str(e), "to_email": message.to_email}


@rabbit_router.subscriber("password_reset_email_queue")
async def process_password_reset_email(
    message: PasswordResetEmailSchema, logger: Logger
):
    """
    Обрабатывает задачу отправки email для сброса пароля.

    Генерирует HTML содержимое на основе шаблона password_reset.html
    и отправляет письмо с ссылкой для сброса пароля.

    Args:
        message (PasswordResetEmailSchema): Сообщение с данными для сброса пароля
            - to_email: Email адрес получателя
            - subject: Тема письма
            - user_name: Имя пользователя
            - reset_token: Токен для генерации ссылки сброса

    Returns:
        Dict[str, Any]: Результат обработки

    Template variables:
        - user_name: Имя пользователя
        - reset_url: Полная ссылка для сброса пароля
    """
    from jinja2 import Environment, FileSystemLoader

    from app.core.settings import settings

    logger.info("📨 Подготовка письма сброса пароля для: %s", message.to_email)

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("password_reset.html")
        reset_url = f"{settings.PASSWORD_RESET_URL}{message.reset_token}"

        html_content = template.render(user_name=message.user_name, reset_url=reset_url)

        await email_manager.send_email(
            to_email=message.to_email, subject=message.subject, body=html_content
        )

        logger.info("✅ Письмо сброса пароля отправлено: %s", message.to_email)
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error("❌ Ошибка при отправке письма сброса пароля: %s", str(e))
        return {"status": "error", "error": str(e), "to_email": message.to_email}


@rabbit_router.subscriber("registration_success_email_queue")
async def process_registration_success_email(
    message: RegistrationSuccessEmailSchema, logger: Logger
):
    """
    Обрабатывает задачу отправки email об успешной регистрации.

    Генерирует HTML содержимое на основе шаблона registration_success.html
    и отправляет приветственное письмо новому пользователю.

    Args:
        message (RegistrationSuccessEmailSchema): Сообщение с данными для регистрации
            - to_email: Email адрес получателя
            - subject: Тема письма
            - user_name: Имя пользователя

    Returns:
        Dict[str, Any]: Результат обработки

    Template variables:
        - user_name: Имя пользователя
        - login_url: Ссылка на страницу входа
    """
    from jinja2 import Environment, FileSystemLoader

    from app.core.settings import settings

    logger.info(
        "📨 Подготовка письма об успешной регистрации для: %s", message.to_email
    )

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("registration_success.html")
        login_url = settings.LOGIN_URL

        html_content = template.render(user_name=message.user_name, login_url=login_url)

        await email_manager.send_email(
            to_email=message.to_email, subject=message.subject, body=html_content
        )

        logger.info(
            "✅ Письмо об успешной регистрации отправлено: %s", message.to_email
        )
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error(
            "❌ Ошибка при отправке письма об успешной регистрации: %s", str(e)
        )
        return {"status": "error", "error": str(e), "to_email": message.to_email}
