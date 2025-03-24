from typing import Any, Optional

from dependencies.register import RepositoryFactory
from models.models import Film
from services.services import BaseInterface

INDEX = "movies"


class FilmService(BaseInterface):
    """Сервис для выполнения операций с данными фильмов."""

    def __init__(self, repository: RepositoryFactory[Film]):
        self.repository = repository.create(Film)

    async def get_by_id(self, film_id: str) -> Film:
        """Получает данные фильма по его идентификатору."""
        return await self.repository.get_by_id(index_name=INDEX, obj_id=film_id)

    async def get_by_search(self, query: Optional[dict[str, Any]]) -> list[Film]:
        """Выполняет поиск фильмов по запросу."""
        return await self.repository.get_by_search(index_name=INDEX, body=query)
