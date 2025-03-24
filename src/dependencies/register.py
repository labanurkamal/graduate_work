from typing import Generic, Type, TypeVar

from pydantic import BaseModel

from services.cache import CacheInterface
from services.services import BaseRepository
from services.storage import StorageInterface

ModelType = TypeVar("ModelType", bound=BaseModel)


class RepositoryFactory(Generic[ModelType]):
    """Класс для создания экземпляров репозиториев."""

    def __init__(self, cache: CacheInterface, storage: StorageInterface):
        self.cache = cache
        self.storage = storage

    def create(self, model: Type[ModelType]):
        """Создает репозиторий для указанной модели."""
        return BaseRepository(cache=self.cache, storage=self.storage, model=model)
