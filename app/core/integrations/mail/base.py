import logging
import smtplib
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

from app.core.settings import settings


class BaseEmailService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.password = settings.SMTP_PASSWORD.get_secret_value()

        template_dir = settings.paths.EMAIL_TEMPLATES_DIR

        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        
    async def send_email(self, to_email: str, subject: str, body: str):
        """
        Отправляет email напрямую через SMTP.

        Args:
            to_email: Email адрес получателя
            subject: Тема письма
            body: HTML-содержимое письма

        Returns:
            bool: True если отправка успешна, False в случае ошибки

        Raises:
            SMTPException: При ошибке отправки через SMTP сервер
        """
        self.logger.info(
            "Отправка email",
            extra={"to_email": to_email, "subject": subject}
        )
        try:
            msg = MIMEText(body, 'html')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = to_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                self.logger.debug("Подключение к SMTP серверу %s:%s",
                              self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.sender_email, self.password)
                server.send_message(msg)

            self.logger.info(
                "Email успешно отправлен",
                extra={"to_email": to_email, "subject": subject}
            )
            return True

        except Exception as e:
            self.logger.error(
                "Ошибка при отправке email: %s", e,
                extra={"to_email": to_email, "subject": subject}
            )
            raise
