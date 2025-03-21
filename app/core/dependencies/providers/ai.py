from dishka import Provider, Scope, provide
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.modules.ai.service import AIService


class AIProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def ai_service(self, db_session: AsyncSession, redis: Redis) -> AIService:
        return AIService(db_session, redis)
