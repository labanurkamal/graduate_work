from typing import Any, Optional

from dependencies.register import RepositoryFactory
from models.models import PersonFilm
from services.services import BaseInterface

INDEX = "persons"


class PersonService(BaseInterface):
    """Сервис для выполнения операций с данными персон."""

    def __init__(self, repository: RepositoryFactory[PersonFilm]):
        self.repository = repository.create(PersonFilm)

    async def get_by_id(self, person_id: str) -> PersonFilm:
        """Получает данные персоны по её идентификатору."""
        return await self.repository.get_by_id(index_name=INDEX, obj_id=person_id)

    async def get_by_search(self, query: Optional[dict[str, Any]]) -> list[PersonFilm]:
        """Выполняет поиск персон по запросу."""
        return await self.repository.get_by_search(index_name=INDEX, body=query)
