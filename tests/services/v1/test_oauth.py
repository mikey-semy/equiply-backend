import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas import OAuthProvider
from app.services.v1.oauth.service import OAuthService
from app.services.v1.auth.service import AuthService
from app.services.v1.users.service import UserService
from app.core.integrations.cache.oauth import OAuthRedisStorage

@pytest.mark.asyncio
async def test_oauth_provider_dependencies():
    # Arrange
    session = AsyncMock()
    auth_service = AsyncMock(spec=AuthService)
    user_service = AsyncMock(spec=UserService)
    redis_storage = MagicMock(spec=OAuthRedisStorage)

    # Act
    service = OAuthService(session)
    service.auth_service = auth_service
    service.user_service = user_service
    service.redis_storage = redis_storage

    provider = service.get_provider(OAuthProvider.GOOGLE)

    # Assert
    assert provider.auth_service == auth_service
    assert provider.user_service == user_service
    assert provider.redis_storage == redis_storage

# Если нужно тестировать через dishka
@pytest.mark.asyncio
@patch('app.core.dependencies.container.get')
async def test_oauth_service_from_dishka(mock_container_get):
    # Arrange
    session = AsyncMock()
    auth_service = AsyncMock(spec=AuthService)
    user_service = AsyncMock(spec=UserService)
    redis_storage = MagicMock(spec=OAuthRedisStorage)

    oauth_service = OAuthService(session)
    oauth_service.auth_service = auth_service
    oauth_service.user_service = user_service
    oauth_service.redis_storage = redis_storage

    mock_container_get.return_value = oauth_service

    # Act
    from app.core.dependencies.container import container
    service = await container.get(OAuthService)
    provider = service.get_provider(OAuthProvider.GOOGLE)

    # Assert
    assert provider.auth_service == auth_service
    assert provider.user_service == user_service
    assert provider.redis_storage == redis_storage
