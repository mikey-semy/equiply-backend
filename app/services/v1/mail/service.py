"""
Модуль для отправки электронных писем.

Этот модуль предоставляет функциональность для отправки электронных писем,
включая простые текстовые сообщения и письма с HTML-шаблонами.
Поддерживает прямую отправку через SMTP и асинхронную отправку через очередь сообщений.
"""
from email.mime.text import MIMEText
import smtplib
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.integrations.messaging.producer import EmailProducer
from app.core.settings import settings
from app.services.v1.base import BaseEmailService

class MailService(BaseEmailService):
    """
    Сервис для отправки электронной почты.

    Предоставляет методы для прямой отправки email и формирования
    писем на основе шаблонов (например, писем верификации).

    Attributes:
        smtp_server: SMTP сервер для отправки писем
        smtp_port: Порт SMTP сервера
        sender_email: Email адрес отправителя
        password: Пароль для SMTP авторизации
        env: Окружение Jinja2 для шаблонов
    """
    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис отправки почты.

        Args:
            session: Сессия базы данных SQLAlchemy
        """
        super().__init__(session)

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

    async def send_verification_email(self, to_email: str, user_name: str, verification_token: str):
        """
        Отправляет email с ссылкой для верификации аккаунта.

        Формирует HTML-письмо на основе шаблона и отправляет его через очередь сообщений,
        что позволяет обрабатывать отправку асинхронно.

        Args:
            to_email: Email адрес получателя
            user_name: Имя пользователя для персонализации письма
            verification_token: Токен для верификации email

        Returns:
            bool: True если задача поставлена в очередь, False в случае ошибки
        """
        self.logger.info(
            "Подготовка письма верификации",
            extra={"to_email": to_email, "user_name": user_name}
        )

        try:
            template = self.env.get_template('verification.html')
            verification_url = f"{settings.VERIFICATION_URL}{verification_token}"

            self.logger.debug(
                "Генерация URL верификации",
                extra={"verification_url": verification_url}
            )

            html_content = template.render(
                user_name=user_name,
                verification_url=verification_url
            )

            self.logger.debug("HTML-контент сгенерирован")

            producer = EmailProducer()
            await producer.send_email_task(
                to_email=to_email,
                subject="Подтверждение email адреса",
                body=html_content
            )

            self.logger.info(
                "Задача на отправку письма верификации поставлена в очередь",
                extra={"to_email": to_email}
            )
            return True

        except Exception as e:
            self.logger.error(
                "Ошибка при подготовке письма верификации: %s", e,
                extra={"to_email": to_email, "user_name": user_name}
            )
            raise
