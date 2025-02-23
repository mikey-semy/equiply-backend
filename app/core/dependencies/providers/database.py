from typing import AsyncGenerator
from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies.connections.database import SessionContextManager

class DatabaseProvider(Provider):
    """
    Провайдер для управления сессиями базы данных.

    Этот провайдер предоставляет доступ к сессии базы данных для запросов.
    Он использует контекстный менеджер для управления сессиями и обеспечивает доступ к сессии в рамках текущего запроса.

    Attributes:
        session (AsyncSession): Сессия базы данных.

    Methods:
        get_session: Возвращает сессию базы данных.
    """
    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncGenerator[AsyncSession, None, None]:
        """
        Возвращает сессию базы данных.

        Returns:
            AsyncSession: Сессия базы данных.

        """
        async with SessionContextManager() as session_manager:
            yield session_manager.session
