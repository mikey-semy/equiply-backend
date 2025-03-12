from typing import Optional

from redis import Redis

class BaseRedisDataManager:
    """
    Базовый класс для работы с Redis.

    Attributes:
        _redis: Экземпляр Redis.

    Methods:
        set: Записывает значение в Redis.
        get: Получает значение из Redis.
        delete: Удаляет значение из Redis.
        sadd: Добавляет значение в множество Redis.
        srem: Удаляет значение из множества Redis.
        smembers: Получает все значения из множества Redis.
        keys: Возвращает список всех ключей в Redis.
    """
    def __init__(self, redis: Redis):
        self._redis = redis

    async def set(self, key: str, value: str, expires: int = None) -> None:
        """
        Записывает значение в Redis.

        Args:
            key: Ключ для записи
            value: Значение для записи
            expires: Время жизни ключа в секундах

        Returns:
            None
        """
        self._redis.set(key, value, ex=expires)

    async def get(self, key: str) -> Optional[str]:
        """
        Получает значение из Redis.

        Args:
            key: Ключ для получения

        Returns:
            Значение из Redis или None, если ключ не найден

        Usage:
            >>> redis_storage = RedisStorage(redis_client)
            >>> redis_storage.set('my_key', 'my_value')
            >>> redis_storage.get('my_key')
            'my_value'
            >>> redis_storage.get('non_existent_key')
            None
        """
        return self._redis.get(key)

    async def delete(self, key: str) -> None:
        """
        Удаляет ключ из Redis.

        Args:
            key: Ключ для удаления

        Returns:
            None

        Usage:
            >>> redis_storage = RedisStorage(redis_client)
            >>> redis_storage.set('my_key', 'my_value')
            >>> redis_storage.get('my_key')
            'my_value'
            >>> redis_storage.delete('my_key')
            >>> redis_storage.get('my_key')
            None
        """
        self._redis.delete(key)

    async def sadd(self, key: str, value: str) -> None:
        """
        Добавляет значение в множество в Redis.

        Args:
            key: Ключ множества
            value: Значение для добавления

        Returns:
            None

        Usage:
            >>> redis_storage = RedisStorage(redis_client)
            >>> redis_storage.sadd('my_set', 'value1')
            >>> redis_storage.sadd('my_set', 'value2')
            >>> redis_storage.sadd('my_set', 'value3')
        """
        self._redis.sadd(key, value)

    async def srem(self, key: str, value: str) -> None:
        """
        Удаляет значение из множества в Redis.

        Args:
            key: Ключ множества
            value: Значение для удаления

        Returns:
            None

        Usage:
        >>> redis_storage = RedisStorage(redis_client)
        >>> redis_storage.sadd('my_set', 'value1')
        >>> redis_storage.sadd('my_set', 'value2')
        >>> redis_storage.sadd('my_set', 'value3')
        >>> redis_storage.srem('my_set', 'value2')
        >>> redis_storage.smembers('my_set')
        ['value1', 'value3']
        """
        self._redis.srem(key, value)

    async def keys(self, pattern: str) -> list[bytes]:
        """
        Получает ключи по паттерну

        Args:
            pattern: Паттерн для поиска ключей

        Returns:
            list[bytes]: Список ключей

        Usage:
            >>> redis_storage.set('key1', 'value1')
            >>> redis_storage.set('key2', 'value2')
            >>> redis_storage.set('key3', 'value3')
            >>> redis_storage.keys('key*')
            ['key1', 'key2', 'key3']
        """
        return self._redis.keys(pattern)

    async def smembers(self, key: str) -> list[str]:
        """
        Получает все элементы множества

        Args:
            key: Ключ множества

        Returns:
            list[str]: Список элементов множества

        Usage:
            >>> redis_storage.sadd('my_set', 'value1')
            >>> redis_storage.sadd('my_set', 'value2')
            >>> redis_storage.sadd('my_set', 'value3')
            >>> redis_storage.smembers('my_set')
            ['value1', 'value2', 'value3']
        """
        result = self._redis.smembers(key)
        return [member.decode() for member in result] if result else []
