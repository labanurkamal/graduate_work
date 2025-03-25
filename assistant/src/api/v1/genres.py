from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies.container import ServiceContainer
from models.models import Genre
from services.genre import GenreService

from . import validators

router = APIRouter()


@router.get(
    "/",
    summary="Получение списка жанров",
    description="Возвращает список всех доступных жанров.",
    response_model=list[Genre],
)
@inject
async def get_genre_list(
    genre_service: GenreService = Depends(Provide[ServiceContainer.genre_service]),
):
    query = {"size": 10_000}
    genre_list = await genre_service.get_by_search(query)
    validators.http_exception(genre_list, HTTPStatus.NOT_FOUND, "Жанры не найдены.")

    return genre_list


@router.get(
    "/{genre_id}/",
    summary="Получение информации о жанре",
    description="Возвращает информацию о жанре по его идентификатору.",
    response_model=Genre,
)
@inject
async def get_genre_details(
    genre_id: str,
    genre_service: GenreService = Depends(Provide[ServiceContainer.genre_service]),
):
    genre = await genre_service.get_by_id(genre_id)
    validators.http_exception(genre, HTTPStatus.NOT_FOUND, "Жанр не найден.")
    return genre
