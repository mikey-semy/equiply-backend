"""
Модуль содержит контейнер зависимостей.

"""
from dishka import make_container
from .providers.database import DatabaseProvider
from .providers.s3 import S3Provider
from .providers.logger import LoggerProvider

container = make_container(
    LoggerProvider(),
    DatabaseProvider(),
    S3Provider(),
)
