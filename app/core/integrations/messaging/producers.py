"""
Модуль производителей сообщений для системы email.

Предоставляет классы для отправки различных типов email сообщений
в очереди RabbitMQ через FastStream.

Классы:
- MessageProducer: Базовый класс для всех производителей
- EmailProducer: Специализированный производитель для email задач

Использование:
    producer = EmailProducer()
    await producer.send_email_task("user@example.com", "Тема", "Текст")
"""
import logging

from app.schemas import (EmailMessageSchema, PasswordResetEmailSchema,
                         RegistrationSuccessEmailSchema,
                         VerificationEmailSchema)

from .broker import broker

logger = logging.getLogger("app.messaging.producers")


class MessageProducer:
    """
    Базовый класс для всех производителей сообщений.

    Предоставляет общий интерфейс для публикации сообщений
    в очереди RabbitMQ через FastStream broker.

    Attributes:
        broker: Экземпляр FastStream брокера для публикации
    """

    async def publish(self, message: dict, queue: str) -> bool:
        """
        Публикует сообщение в указанную очередь.

        Args:
            message (Dict[Any, Any]): Сообщение для публикации (должно быть сериализуемым)
            queue (str): Имя очереди в RabbitMQ

        Returns:
            bool: True если сообщение успешно опубликовано

        Raises:
            Exception: При ошибке публикации сообщения
        """
        try:
            await broker.publish(message, queue)
            logger.info("Сообщение отправлено в очередь: %s", queue)
            return True
        except Exception as e:
            logger.error(
                "Ошибка при отправке сообщения в очередь %s: %s", queue, str(e)
            )
            raise


class EmailProducer(MessageProducer):
    """
    Производитель сообщений для отправки задач по электронной почте.

    Специализированный класс для создания и отправки различных типов
    email сообщений в соответствующие очереди RabbitMQ.

    Поддерживаемые типы email:
    - Обычные email сообщения
    - Письма верификации
    - Письма сброса пароля
    - Письма об успешной регистрации

    Примеры использования:
        producer = EmailProducer()

        # Обычное письмо
        await producer.send_email_task(
            to_email="user@example.com",
            subject="Тема",
            body="<h1>HTML содержимое</h1>"
        )

        # Письмо верификации
        await producer.send_verification_email(
            to_email="user@example.com",
            verification_token="abc123"
        )
    """

    async def send_email_task(self, to_email: str, subject: str, body: str) -> bool:
        """
        Отправляет задачу на отправку обычного электронного письма.

        Args:
            to_email (str): Email адрес получателя
            subject (str): Тема письма
            body (str): Содержимое письма (HTML или текст)

        Returns:
            bool: True если задача успешно поставлена в очередь

        Raises:
            Exception: При ошибке отправки в очередь
        """
        message = EmailMessageSchema(to_email=to_email, subject=subject, body=body)

        return await self.publish(message.model_dump(), "email_queue")

    async def send_verification_email(
        self, to_email: str, user_name: str, verification_token: str
    ) -> bool:
        """
        Отправляет задачу на отправку письма верификации.

        Создает сообщение для верификации email адреса с токеном.
        HTML содержимое будет сгенерировано в consumer на основе шаблона.

        Args:
            to_email (str): Email адрес получателя
            verification_token (str): Уникальный токен для верификации

        Returns:
            bool: True если задача успешно поставлена в очередь

        Raises:
            Exception: При ошибке отправки в очередь
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
        Отправляет задачу на отправку письма сброса пароля.

        Args:
            to_email (str): Email адрес получателя
            user_name (str): Имя пользователя для персонализации
            reset_token (str): Токен для сброса пароля

        Returns:
            bool: True если задача успешно поставлена в очередь

        Raises:
            Exception: При ошибке отправки в очередь
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
        Отправляет задачу на отправку письма об успешной регистрации.

        Args:
            to_email (str): Email адрес получателя
            user_name (str): Имя пользователя для персонализации

        Returns:
            bool: True если задача успешно поставлена в очередь

        Raises:
            Exception: При ошибке отправки в очередь
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
