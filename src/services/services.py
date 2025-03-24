import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar

from pydantic import BaseModel

from .cache import CacheInterface
from .storage import StorageInterface

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 3

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseInterface(ABC):
    """
    Абстрактный интерфейс для взаимодействия с данными.
    """

    @abstractmethod
    async def get_by_id(self, *args, **kwargs):
        """Получает объект по его идентификатору."""
        pass

    @abstractmethod
    async def get_by_search(self, *args, **kwargs):
        """Выполняет поиск объектов по запросу."""
        pass


class BaseRepository(BaseInterface, Generic[ModelType]):
    """Базовая реализация репозитория для работы с данными."""

    def __init__(
        self, cache: CacheInterface, storage: StorageInterface, model: Type[ModelType]
    ):
        self.cache = cache
        self.storage = storage
        self._model = model

    async def get_by_id(self, index_name: str, obj_id: str) -> Optional[ModelType]:
        """Получает объект по идентификатору из кэша или хранилища."""
        cache_key = self._get_cache_key(index_name, obj_id)
        cached_data = await self.cache.get(name=cache_key)

        if cached_data:
            return self._model.model_validate(cached_data)

        storage_data = await self.storage.get(index=index_name, id=obj_id)
        if not storage_data:
            return None

        model_instance = self._model(**storage_data)
        await self.cache.set(
            name=cache_key,
            value=model_instance.model_dump_json(),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS,
        )

        return model_instance

    async def get_by_search(
        self, index_name: str, body: dict[str, Any] = None
    ) -> Optional[list[ModelType]]:
        """Выполняет поиск объектов по запросу в кэше или хранилище."""
        cache_key = self._get_cache_key_for_query(index_name, body)
        cached_data = await self.cache.get(name=cache_key)

        if cached_data:
            return [self._model.model_validate(data) for data in cached_data]

        storage_data = await self.storage.search(index=index_name, body=body)
        if not storage_data:
            return None

        model_instance = [self._model(**doc["_source"]) for doc in storage_data]
        await self.cache.set(
            name=cache_key,
            value=json.dumps([model.model_dump() for model in model_instance]),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS,
        )

        return model_instance

    @staticmethod
    def _get_cache_key_for_query(index_name: str, body: dict[str, Any]) -> str:
        """Генерирует ключ для кэша на основе запроса."""
        query_string = json.dumps(body, sort_keys=True)
        query_hash = hashlib.md5(query_string.encode()).hexdigest()

        return f"{index_name}:query:{query_hash}"

    @staticmethod
    def _get_cache_key(index_name: str, obj_id: str) -> str:
        """Генерирует ключ для кэша на основе идентификатора объекта."""
        return f"{index_name}:{obj_id}"
