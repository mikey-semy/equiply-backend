"""
Модуль содержит контейнер зависимостей.
"""
from dishka.integrations.fastapi import FastapiProvider
from dishka import make_async_container

from .providers.pagination import PaginationProvider
from .providers.database import DatabaseProvider
from .providers.messaging import RabbitMQProvider
from .providers.cache import RedisProvider, RedisMiddlewareProvider
from .providers.storage import S3Provider
from .providers.auth import AuthProvider
from .providers.oauth import OAuthProvider
from .providers.register import RegisterProvider
from .providers.users import UserProvider
from .providers.profile import ProfileProvider
from .providers.workspaces import WorkspaceProvider

container = make_async_container(
    FastapiProvider(),
    PaginationProvider(),
    DatabaseProvider(),
    RabbitMQProvider(),
    RedisProvider(),
    RedisMiddlewareProvider(),
    S3Provider(),
    AuthProvider(),
    OAuthProvider(),
    RegisterProvider(),
    UserProvider(),
    ProfileProvider(),
    WorkspaceProvider(),
)
