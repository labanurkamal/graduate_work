from abc import ABC, abstractmethod
from typing import Any, Union

from elasticsearch import AsyncElasticsearch, NotFoundError


class StorageInterface(ABC):
    """
    Абстрактный интерфейс для работы с хранилищем данных.
    """

    @abstractmethod
    async def get(self, *args, **kwargs: Any):
        """Получает данные по заданным аргументам."""
        pass

    @abstractmethod
    async def search(self, *args, **kwargs: Any):
        """Выполняет поиск по заданным аргументам."""
        pass


class ElasticStorageRepository(StorageInterface):
    """Реализация интерфейса для работы с хранилищем Elasticsearch."""

    def __init__(self, storage: AsyncElasticsearch) -> None:
        self.storage = storage

    async def get(self, index: str, id: str) -> Union[dict[str, Any], None]:
        """Получает документ из Elasticsearch по индексу и идентификатору."""
        try:
            doc = await self.storage.get(index=index, id=id)
        except NotFoundError:
            return None

        return doc["_source"]

    async def search(self, index: str, body: Any) -> Union[list[dict[str, Any]], None]:
        """Выполняет поиск по индексу в Elasticsearch."""
        try:
            docs = await self.storage.search(index=index, body=body)
        except NotFoundError:
            return None

        return docs["hits"]["hits"]
