from typing import AsyncGenerator
from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.connections.database import DatabaseContextManager

class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with DatabaseContextManager() as session:
            yield session
