import json
from aio_pika import Message, connect_robust
from app.core.settings import settings

class EmailProducer:
    """
    Производитель сообщений для отправки задач по электронной почте в очередь RabbitMQ.

    EmailProducer позволяет асинхронно ставить задачи на отправку email
    в очередь RabbitMQ для последующей обработки потребителем.
    Это позволяет отделить логику отправки писем от основного потока выполнения
    приложения и обеспечить надежную доставку даже при высоких нагрузках.

    Attributes:
        connection: Соединение с RabbitMQ
        channel: Канал для взаимодействия с RabbitMQ
        queue_name: Название очереди сообщений (по умолчанию "email_queue")
    """
    def __init__(self):
        """
        Инициализирует производителя сообщений для отправки email.
        """
        self.connection = None
        self.channel = None
        self.queue_name = "email_queue"

    async def connect(self):
        """
        Устанавливает соединение с RabbitMQ и создает очередь сообщений.

        Создает подключение, канал и объявляет очередь для отправки сообщений.
        """
        self.connection = await connect_robust(**settings.rabbitmq_params)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(self.queue_name)

    async def send_email_task(self, to_email: str, subject: str, body: str):
        """
        Отправляет задачу на отправку электронного письма в очередь RabbitMQ.

        Формирует сообщение с данными для отправки email и публикует его
        в очередь RabbitMQ для последующей обработки потребителем.

        Args:
            to_email (str): Email адрес получателя
            subject (str): Тема письма
            body (str): Содержимое письма (HTML или текст)

        Note:
            Метод автоматически устанавливает соединение, если оно еще не установлено.
        """
        if not self.connection:
            await self.connect()

        message = {
            "to_email": to_email,
            "subject": subject,
            "body": body
        }

        await self.channel.default_exchange.publish(
            Message(json.dumps(message).encode()),
            routing_key=self.queue_name
        )
