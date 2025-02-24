from typing import AsyncGenerator
from aiologger import Logger
from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies.connections.database import DatabaseContextManager

class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(self, logger: Logger) -> AsyncGenerator[AsyncSession, None]:
        async with DatabaseContextManager(logger) as session:
            yield session
