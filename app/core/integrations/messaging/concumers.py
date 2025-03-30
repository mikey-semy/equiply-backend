import logging
from faststream.rabbit.fastapi import Logger

from app.schemas import EmailMessageSchema, VerificationEmailSchema, PasswordResetEmailSchema, RegistrationSuccessEmailSchema
from app.core.integrations.mail.base import BaseEmailDataManager

from .broker import rabbit_router

logger = logging.getLogger("app.email.tasks")
logger.info("✨ Модуль consumers.py загружен")
email_manager = BaseEmailDataManager()

@rabbit_router.subscriber("email_queue")
async def process_email(message: EmailMessageSchema, logger: Logger):
    """
    Обрабатывает задачу отправки email

    Args:
        message (EmailMessageSchema): Сообщение с данными для отправки email
        logger (Logger): Логгер для записи информации об обработке
    """
    logger.info(f"📨 Обработка email для: {message.to_email}")

    try:
        await email_manager.send_email(
            to_email=message.to_email,
            subject=message.subject,
            body=message.body
        )
        logger.info(f"✅ Email успешно отправлен: {message.to_email}")
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке email: {str(e)}")
        return {"status": "error", "error": str(e), "to_email": message.to_email}

@rabbit_router.subscriber("verification_email_queue")
async def process_verification_email(message: VerificationEmailSchema, logger: Logger):
    """
    Обрабатывает задачу отправки email для верификации

    Args:
        message (VerificationEmailSchema): Сообщение с данными для отправки email
        logger (Logger): Логгер для записи информации об обработке
    """
    from jinja2 import Environment, FileSystemLoader
    from app.core.settings import settings

    logger.info(f"📨 Подготовка письма верификации для: {message.to_email}")

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("verification.html")
        verification_url = f"{settings.VERIFICATION_URL}{message.verification_token}"

        html_content = template.render(
            user_name=message.user_name,
            verification_url=verification_url
        )

        await email_manager.send_email(
            to_email=message.to_email,
            subject=message.subject,
            body=html_content
        )

        logger.info(f"✅ Письмо верификации отправлено: {message.to_email}")
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке письма верификации: {str(e)}")
        return {"status": "error", "error": str(e), "to_email": message.to_email}

@rabbit_router.subscriber("password_reset_email_queue")
async def process_password_reset_email(message: PasswordResetEmailSchema, logger: Logger):
    """
    Обрабатывает задачу отправки email для сброса пароля

    Args:
        message (PasswordResetEmailSchema): Сообщение с данными для отправки email
        logger (Logger): Логгер для записи информации об обработке
    """
    from jinja2 import Environment, FileSystemLoader
    from app.core.settings import settings

    logger.info(f"📨 Подготовка письма сброса пароля для: {message.to_email}")

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("password_reset.html")
        reset_url = f"{settings.PASSWORD_RESET_URL}{message.reset_token}"

        html_content = template.render(
            user_name=message.user_name,
            reset_url=reset_url
        )

        await email_manager.send_email(
            to_email=message.to_email,
            subject=message.subject,
            body=html_content
        )

        logger.info(f"✅ Письмо сброса пароля отправлено: {message.to_email}")
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке письма сброса пароля: {str(e)}")
        return {"status": "error", "error": str(e), "to_email": message.to_email}

@rabbit_router.subscriber("registration_success_email_queue")
async def process_registration_success_email(message: RegistrationSuccessEmailSchema, logger: Logger):
    """
    Обрабатывает задачу отправки email об успешной регистрации

    Args:
        message (RegistrationSuccessEmailSchema): Сообщение с данными для отправки email
        logger (Logger): Логгер для записи информации об обработке
    """
    from jinja2 import Environment, FileSystemLoader
    from app.core.settings import settings

    logger.info(f"📨 Подготовка письма об успешной регистрации для: {message.to_email}")

    try:
        template_dir = settings.paths.EMAIL_TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        template = env.get_template("registration_success.html")
        login_url = settings.LOGIN_URL

        html_content = template.render(
            user_name=message.user_name,
            login_url=login_url
        )

        await email_manager.send_email(
            to_email=message.to_email,
            subject=message.subject,
            body=html_content
        )

        logger.info(f"✅ Письмо об успешной регистрации отправлено: {message.to_email}")
        return {"status": "success", "to_email": message.to_email}
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке письма об успешной регистрации: {str(e)}")
        return {"status": "error", "error": str(e), "to_email": message.to_email}
