from http import HTTPStatus
from typing import Literal, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from dependencies.container import ServiceContainer
from models.models import Film
from services.film import FilmService

from . import validators
from .models import ShortFilm
from .paginations import PaginationParams

router = APIRouter()


@router.get(
    "/",
    summary="Получить популярные фильмы или фильмы по жанру",
    description="Этот эндпоинт возвращает список популярных фильмов или фильмов, отфильтрованных по жанру.",
    responses={
        HTTPStatus.OK.value: {"description": "Список фильмов успешно получен"},
        HTTPStatus.NOT_FOUND.value: {"description": "Фильмы не найдены"},
    },
    response_model=list[ShortFilm],
)
@inject
async def get_popular_or_by_genre_films(
    film_service: FilmService = Depends(Provide[ServiceContainer.film_service]),
    genre: Optional[str] = Query(None, description="ID жанра для фильтрации фильмов"),
    sort: Optional[Literal["-imdb_rating", "imdb_rating"]] = Query(
        "-imdb_rating",
        description="Поле для сортировки фильмов. Используйте '-' для обратного порядка.",
    ),
    pg: PaginationParams = Depends(PaginationParams),
) -> list[ShortFilm]:
    query = {
        "query": {
            "nested": {
                "path": "genre",
                "query": {
                    "bool": {"must": [{"term": {"genre.id": genre}}] if genre else []}
                },
            }
        },
        "sort": [
            {sort.lstrip("-"): {"order": "desc" if sort.startswith("-") else "asc"}}
        ],
        "from": pg.page_size * (pg.page_number - 1),
        "size": pg.page_size,
    }
    list_film = await film_service.get_by_search(query)
    validators.http_exception(list_film, HTTPStatus.NOT_FOUND, "Фильмы не найдены")

    return list_film


@router.get(
    "/search/",
    summary="Поиск фильмов",
    description="Этот эндпоинт позволяет искать фильмы по названию или описанию.",
    responses={
        HTTPStatus.OK.value: {"description": "Фильмы найдены по запросу"},
        HTTPStatus.NOT_FOUND.value: {"description": "Фильмы по запросу не найдены"},
    },
    response_model=list[ShortFilm],
)
@inject
async def get_film_search(
    film_service: FilmService = Depends(Provide[ServiceContainer.film_service]),
    query: str = Query(..., description="Поисковый запрос для фильмов"),
    pg: PaginationParams = Depends(PaginationParams),
) -> list[ShortFilm]:
    search_query = {
        "query": {"multi_match": {"query": query, "fields": ["title", "description"]}},
        "from": pg.page_size * (pg.page_number - 1),
        "size": pg.page_size,
    }

    film = await film_service.get_by_search(search_query)
    validators.http_exception(
        film, HTTPStatus.NOT_FOUND, "Фильмы по запросу не найдены."
    )
    return film


@router.get(
    "/{film_id}/",
    summary="Получить детали фильма",
    description="Этот эндпоинт возвращает информацию о фильме по его ID.",
    responses={
        HTTPStatus.OK.value: {"description": "Информация о фильме найдена"},
        HTTPStatus.NOT_FOUND.value: {"description": "Фильм не найден"},
    },
    response_model=Film,
)
@inject
async def get_film_details(
    film_id: str,
    film_service: FilmService = Depends(Provide[ServiceContainer.film_service]),
) -> Film:
    film = await film_service.get_by_id(film_id)
    validators.http_exception(film, HTTPStatus.NOT_FOUND, "Фильм не найден.")

    return film
