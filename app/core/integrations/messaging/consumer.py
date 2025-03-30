import logging
import json

from aio_pika import connect_robust

from app.core.integrations.mail import BaseEmailDataManager
from app.core.settings import settings

class EmailConsumer:
    """
    Потребитель сообщений из очереди RabbitMQ для асинхронной отправки электронных писем.

    EmailConsumer подключается к очереди RabbitMQ, извлекает сообщения с задачами
    на отправку email и обрабатывает их с помощью BaseEmailDataManager.

    Параметр session используется для передачи в BaseEmailDataManager, который может
    сохранять логи отправки, получать шаблоны писем из базы данных или
    проверять данные пользователей.

    Attributes:
        connection: Соединение с RabbitMQ
        channel: Канал для взаимодействия с RabbitMQ
        queue_name: Название очереди сообщений (по умолчанию "email_queue")
        data_manager: Сервис для отправки электронных писем
    """

    def __init__(self):
        """
        Инициализирует потребителя электронных сообщений.
        """
        self.connection = None
        self.channel = None
        self.queue = None
        self.queue_name = "email_queue"
        self.data_manager = BaseEmailDataManager()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self):
        """
        Устанавливает соединение с RabbitMQ и создает очередь сообщений.

        Создает подключение, канал и объявляет очередь для получения сообщений.
        """
        self.connection = await connect_robust(**settings.rabbitmq_params)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name)

    async def process_message(self, message):
        """
        Обрабатывает полученное сообщение из очереди.

        Извлекает данные из сообщения (email получателя, тема, содержимое)
        и вызывает BaseEmailDataManager для фактической отправки письма.

        Args:
            message: Сообщение из очереди RabbitMQ
        """
        try:
            body = json.loads(message.body.decode())
            self.logger.info("📨 Получено сообщение: %s", body['to_email'])

            async with message.process():
                await self.data_manager.send_email(
                    to_email=body["to_email"],
                    subject=body["subject"],
                    body=body["body"]
                )
                self.logger.info("✅ Письмо отправлено: %s", body['to_email'])
        except Exception as e:
            self.logger.error("❌ Ошибка при обработке сообщения: %s", e)

    async def run(self):
        """
        Запускает бесконечный цикл обработки сообщений из очереди.

        Подключается к RabbitMQ, если соединение еще не установлено,
        и начинает обрабатывать сообщения по мере их поступления.
        """
        if not self.connection:
            await self.connect()

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.process_message(message)
