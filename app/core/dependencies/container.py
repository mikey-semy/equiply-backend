"""
Модуль содержит контейнер зависимостей.
"""

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider
from .providers.admin import AdminProvider
from .providers.ai import AIProvider
from .providers.auth import AuthProvider
from .providers.cache import RedisMiddlewareProvider, RedisProvider
from .providers.database import DatabaseProvider
from .providers.messaging import RabbitMQProvider
from .providers.oauth import OAuthProvider
from .providers.pagination import PaginationProvider
from .providers.profile import ProfileProvider
from .providers.register import RegisterProvider
from .providers.storage import S3Provider
from .providers.users import UserProvider
from .providers.workspaces import WorkspaceProvider

container = make_async_container(
    AdminProvider(),
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
    AIProvider(),
)
