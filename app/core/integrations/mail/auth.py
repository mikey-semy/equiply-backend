"""
Модуль для отправки электронных писем, связанных с аутентификацией и регистрацией.

Предоставляет функциональность для отправки писем верификации,
сброса пароля и уведомлений об успешной регистрации.
"""

from app.core.integrations.mail.base import BaseEmailDataManager
from app.core.integrations.messaging.producer import EmailProducer
from app.core.settings import settings


class AuthEmailDataManager(BaseEmailDataManager):
    """
    Сервис для отправки писем, связанных с аутентификацией и регистрацией.

    Предоставляет методы для формирования и отправки писем верификации,
    сброса пароля и уведомлений об успешной регистрации.
    """

    async def send_verification_email(
        self, to_email: str, user_name: str, verification_token: str
    ):
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
            extra={"to_email": to_email, "user_name": user_name},
        )

        try:
            template = self.env.get_template("verification.html")
            verification_url = f"{settings.VERIFICATION_URL}{verification_token}"

            self.logger.debug(
                "Генерация URL верификации",
                extra={"verification_url": verification_url},
            )

            html_content = template.render(
                user_name=user_name, verification_url=verification_url
            )

            self.logger.debug("HTML-контент сгенерирован")

            producer = EmailProducer()
            await producer.send_email_task(
                to_email=to_email,
                subject="Подтверждение email адреса",
                body=html_content,
            )

            self.logger.info(
                "Задача на отправку письма верификации поставлена в очередь",
                extra={"to_email": to_email},
            )
            return True

        except Exception as e:
            self.logger.error(
                "Ошибка при подготовке письма верификации: %s",
                e,
                extra={"to_email": to_email, "user_name": user_name},
            )
            raise

    async def send_password_reset_email(
        self, to_email: str, user_name: str, reset_token: str
    ):
        """
        Отправляет email со ссылкой для сброса пароля.

        Args:
            to_email: Email адрес получателя
            user_name: Имя пользователя для персонализации письма
            reset_token: Токен для сброса пароля

        Returns:
            bool: True если задача поставлена в очередь, False в случае ошибки
        """
        self.logger.info(
            "Подготовка письма для сброса пароля",
            extra={"to_email": to_email, "user_name": user_name},
        )

        try:
            template = self.env.get_template("password_reset.html")
            reset_url = f"{settings.PASSWORD_RESET_URL}{reset_token}"

            self.logger.debug(
                "Генерация URL для сброса пароля", extra={"reset_url": reset_url}
            )

            html_content = template.render(user_name=user_name, reset_url=reset_url)

            self.logger.debug("HTML-контент для сброса пароля сгенерирован")

            producer = EmailProducer()
            await producer.send_email_task(
                to_email=to_email, subject="Восстановление пароля", body=html_content
            )

            self.logger.info(
                "Задача на отправку письма для сброса пароля поставлена в очередь",
                extra={"to_email": to_email},
            )
            return True

        except Exception as e:
            self.logger.error(
                "Ошибка при подготовке письма для сброса пароля: %s",
                e,
                extra={"to_email": to_email, "user_name": user_name},
            )
            raise

    async def send_registration_success_email(self, to_email: str, user_name: str):
        """
        Отправляет уведомление об успешной регистрации.

        Args:
            to_email: Email адрес получателя
            user_name: Имя пользователя для персонализации письма

        Returns:
            bool: True если задача поставлена в очередь, False в случае ошибки
        """
        self.logger.info(
            "Подготовка письма об успешной регистрации",
            extra={"to_email": to_email, "user_name": user_name},
        )

        try:
            template = self.env.get_template("registration_success.html")
            login_url = settings.LOGIN_URL

            html_content = template.render(user_name=user_name, login_url=login_url)

            self.logger.debug("HTML-контент об успешной регистрации сгенерирован")

            producer = EmailProducer()
            await producer.send_email_task(
                to_email=to_email,
                subject="Регистрация успешно завершена",
                body=html_content,
            )

            self.logger.info(
                "Задача на отправку письма об успешной регистрации поставлена в очередь",
                extra={"to_email": to_email},
            )
            return True

        except Exception as e:
            self.logger.error(
                "Ошибка при подготовке письма об успешной регистрации: %s",
                e,
                extra={"to_email": to_email, "user_name": user_name},
            )
            raise
