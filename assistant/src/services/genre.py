from typing import Any, Optional

from dependencies.register import RepositoryFactory
from models.models import Genre
from services.services import BaseInterface

INDEX = "genres"


class GenreService(BaseInterface):
    """Сервис для выполнения операций с данными жанров."""

    def __init__(self, repository: RepositoryFactory[Genre]) -> None:
        self.repository = repository.create(Genre)

    async def get_by_id(self, genre_id: str) -> Genre:
        """Получает данные жанра по его идентификатору."""
        return await self.repository.get_by_id(index_name=INDEX, obj_id=genre_id)

    async def get_by_search(self, query: Optional[dict[str, Any]]) -> list[Genre]:
        """Выполняет поиск жанров по запросу."""
        return await self.repository.get_by_search(index_name=INDEX, body=query)
