from enum import Enum
from typing import Dict, Any

from pydantic import BaseModel

class IntentHandlers(str, Enum):
    film_description = "{response}"
    film_rating = "Фильм {entity_name} получил рейтинг {response} из 10"
    actor_info = "Актеры снявшиеся фильме {entity_name} это {response}: ..."
    director_info = "Режиссеры снявшие фильм {entity_name}: {response}: ..."
    writer_info = "Сценаристы, который написал сценарий фильма {entity_name}: {response}: ..."
    actor_movies = "Актер {entity_name} снимался фильмах: {response}: ..."
    director_movies = "Режиссера {entity_name} к фильмографию входит: {response}: ..."

class IntentFields(str, Enum):
    film_description = 'description'
    film_rating = 'imdb_rating'
    actor_info = 'actors'
    director_info = 'directors'
    writer_info = 'writers'
    actor_movies = 'films'
    director_movies = 'films'


class EntityType(str, Enum):
    GENRE = 'GENRE'
    PERSON = 'PERSON'
    FILM = 'FILM'


class AssistantYandexRequest(BaseModel):
    meta: Dict[str, Any]
    session: Dict[str, Any]
    request: Dict[str, Any]
    version: str

class AssistantYandexResponse(BaseModel):
    version: str
    session: Dict[str, Any]
    response: Dict[str, Any]