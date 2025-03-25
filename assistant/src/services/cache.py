import json
from abc import ABC, abstractmethod
from typing import Any, Union

from redis.asyncio import Redis


class CacheInterface(ABC):
    """Абстрактный интерфейс для взаимодействия с кэшем."""

    @abstractmethod
    async def get(self, *args, **kwargs):
        """Асинхронно получает данные из кэша."""
        pass

    @abstractmethod
    async def set(self, *args, **kwargs):
        """Асинхронно записывает данные в кэш."""
        pass


class RedisCacheRepository(CacheInterface):
    """Реализация интерфейса CacheInterface для работы с Redis."""

    def __init__(self, cache: Redis) -> None:
        self.cache = cache

    async def get(self, name: str) -> Union[dict[str, Any], None]:
        """Получает данные из кэша по имени."""
        cached_data = await self.cache.get(name)
        if not cached_data:
            return None

        return json.loads(cached_data)

    async def set(self, name: str, value: Any, ex: int = None) -> None:
        """Сохраняет данные в кэш."""
        await self.cache.set(name, value, ex)
