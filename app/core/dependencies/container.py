"""
Модуль содержит контейнер зависимостей.
"""

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider

from .providers.access import AccessProvider
from .providers.admin import AdminProvider
from .providers.ai import AIProvider
from .providers.auth import AuthProvider
from .providers.cache import RedisMiddlewareProvider, RedisProvider
from .providers.database import DatabaseProvider
from .providers.kanban import KanbanProvider
from .providers.messaging import RabbitMQProvider
from .providers.oauth import OAuthProvider
from .providers.pagination import PaginationProvider
from .providers.profile import ProfileProvider
from .providers.register import RegisterProvider
from .providers.storage import S3Provider
from .providers.users import UserProvider
from .providers.groups import GroupProvider
from .providers.workspaces import WorkspaceProvider
from .providers.tables import TableProvider

container = make_async_container(
    AccessProvider(),
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
    GroupProvider(),
    ProfileProvider(),
    WorkspaceProvider(),
    AIProvider(),
    KanbanProvider(),
    TableProvider()
)
