"""
Модуль для отправки электронных писем, связанных с аутентификацией и регистрацией.

Предоставляет функциональность для отправки писем верификации,
сброса пароля и уведомлений об успешной регистрации.
"""

from app.core.integrations.mail.base import BaseEmailDataManager
from app.core.integrations.messaging import EmailProducer

class AuthEmailDataManager(BaseEmailDataManager):
    """
    Сервис для отправки писем, связанных с аутентификацией и регистрацией.

    Предоставляет методы для формирования и отправки писем верификации,
    сброса пароля и уведомлений об успешной регистрации.
    """
    def __init__(self):
        super().__init__()
        self.producer = EmailProducer()

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
            return await self.producer.send_verification_email(
                to_email=to_email,
                user_name=user_name,
                verification_token=verification_token
            )
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
            return await self.producer.send_password_reset_email(
                to_email=to_email,
                user_name=user_name,
                reset_token=reset_token
            )
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
            return await self.producer.send_registration_success_email(
                to_email=to_email,
                user_name=user_name
            )
        except Exception as e:
            self.logger.error(
                "Ошибка при подготовке письма об успешной регистрации: %s",
                e,
                extra={"to_email": to_email, "user_name": user_name},
            )
            raise
