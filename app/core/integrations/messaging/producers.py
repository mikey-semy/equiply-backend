import logging

from app.schemas import (EmailMessageSchema, PasswordResetEmailSchema,
                         RegistrationSuccessEmailSchema,
                         VerificationEmailSchema)

from .broker import broker

logger = logging.getLogger("app.messaging.producers")


class MessageProducer:
    """
    Базовый класс для всех производителей сообщений.
    """

    async def publish(self, message: dict, queue: str) -> bool:
        """
        Публикует сообщение в указанную очередь.

        Args:
            message: Сообщение для публикации
            queue: Имя очереди

        Returns:
            bool: True если сообщение успешно опубликовано
        """
        try:
            await broker.publish(message, queue)
            logger.info("Сообщение отправлено в очередь: %s", queue)
            return True
        except Exception as e:
            logger.error("Ошибка при отправке сообщения в очередь %s: %s", queue, str(e))
            raise

class EmailProducer(MessageProducer):
    """
    Производитель сообщений для отправки задач по электронной почте через FastStream.

    EmailProducer позволяет асинхронно ставить задачи на отправку email
    в очередь RabbitMQ для последующей обработки потребителем.
    """

    async def send_email_task(self, to_email: str, subject: str, body: str) -> bool:
        """
        Отправляет задачу на отправку электронного письма в очередь RabbitMQ.

        Args:
            to_email (str): Email адрес получателя
            subject (str): Тема письма
            body (str): Содержимое письма (HTML или текст)
        """
        message = EmailMessageSchema(to_email=to_email, subject=subject, body=body)

        return await self.publish(message.model_dump(), "email_queue")

    async def send_verification_email(
        self, to_email: str, user_name: str, verification_token: str
    ) -> bool:
        """
        Отправляет задачу на отправку письма верификации в очередь RabbitMQ.

        Args:
            to_email (str): Email адрес получателя
            user_name (str): Имя пользователя
            verification_token (str): Токен верификации
        """
        message = VerificationEmailSchema(
            to_email=to_email,
            subject="Подтверждение email адреса",
            body="",  # Будет заполнено в обработчике
            user_name=user_name,
            verification_token=verification_token,
        )

        return await self.publish(message.model_dump(), "verification_email_queue")

    async def send_password_reset_email(
        self, to_email: str, user_name: str, reset_token: str
    ) -> bool:
        """
        Отправляет задачу на отправку письма сброса пароля в очередь RabbitMQ.

        Args:
            to_email (str): Email адрес получателя
            user_name (str): Имя пользователя
            reset_token (str): Токен сброса пароля
        """
        message = PasswordResetEmailSchema(
            to_email=to_email,
            subject="Восстановление пароля",
            body="",  # Будет заполнено в обработчике
            user_name=user_name,
            reset_token=reset_token,
        )

        return await self.publish(message.model_dump(), "password_reset_email_queue")

    async def send_registration_success_email(
        self, to_email: str, user_name: str
    ) -> bool:
        """
        Отправляет задачу на отправку письма об успешной регистрации в очередь RabbitMQ.

        Args:
            to_email (str): Email адрес получателя
            user_name (str): Имя пользователя
        """
        message = RegistrationSuccessEmailSchema(
            to_email=to_email,
            subject="Регистрация успешно завершена",
            body="",  # Будет заполнено в обработчике
            user_name=user_name,
        )

        return await self.publish(
            message.model_dump(), "registration_success_email_queue"
        )
