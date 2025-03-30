"""
Инициализация брокера сообщений RabbitMQ через FastStream.
"""
from faststream.rabbit.fastapi import RabbitRouter
from app.core.settings import settings

rabbit_router = RabbitRouter(
    settings.rabbitmq_dsn,
    reconnect_interval=5.0,
)

broker = rabbit_router.broker
