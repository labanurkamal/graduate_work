from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from dependencies.container import ServiceContainer
from services.person import PersonService

from . import validators
from .models import PersonFilm, ShortFilm
from .paginations import PaginationParams

router = APIRouter()


@router.get(
    "/search/",
    summary="Поиск по персонажам",
    description="Ищет персонажей по имени. Возвращает список персонажей с их фильмами.",
    response_model=list[PersonFilm],
)
@inject
async def get_person_search(
        person_service: PersonService = Depends(Provide[ServiceContainer.person_service]),
        query: Optional[str] = Query(..., description="Имя персонажа для поиска."),
        pg: PaginationParams = Depends(PaginationParams),
) -> list[PersonFilm]:
    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "full_name",
                ],
            }
        },
        "from": pg.page_size * (pg.page_number - 1),
        "size": pg.page_size,
    }
    person_search = await person_service.get_by_search(search_query)
    validators.http_exception(
        person_search, HTTPStatus.NOT_FOUND, "Персонажи не найдены."
    )

    return person_search


@router.get(
    "/{person_id}/",
    summary="Получение информации о персонаже",
    description="Возвращает полную информацию о персонаже по его идентификатору.",
    response_model=PersonFilm,
)
@inject
async def get_person_details(
        person_id: str,
        person_service: PersonService = Depends(Provide[ServiceContainer.person_service]),
) -> PersonFilm:
    person = await person_service.get_by_id(person_id)
    validators.http_exception(person, HTTPStatus.NOT_FOUND, "Персонаж не найден.")

    return person


@router.get(
    "/{person_id}/film/",
    summary="Получение фильмов персонажа",
    description="Возвращает список фильмов, в которых снялся персонаж по его идентификатору.",
    response_model=list[ShortFilm],
)
@inject
async def get_person_film(
        person_id: str,
        person_service: PersonService = Depends(Provide[ServiceContainer.person_service]),
) -> list[ShortFilm]:
    person_films = await person_service.get_by_id(person_id)
    validators.http_exception(
        person_films, HTTPStatus.NOT_FOUND, "Фильмов персонажа не найден."
    )
    return person_films.films
