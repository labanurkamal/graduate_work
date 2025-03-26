import uuid
from http import HTTPStatus

import pytest

from tests.funct.settings import test_settings

FILM_PATH_ROOT = f"{test_settings.service_settings.get_api_v1()}/films"
INDEX = "movies"
SCHEME = test_settings.es_settings.get_indices_mapping()[INDEX]


@pytest.mark.asyncio
class TestFilm:
    """
    Набор тестов для проверки успешной работы API, связанного с фильмами.
    Тесты включают:
    - Получение популярных фильмов по жанру.
    - Сортировку фильмов по рейтингу.
    - Поиск фильмов по запросу.
    - Получение конкретного фильма по ID.
    """

    @staticmethod
    async def cleaning_es_cache(es_client):
        """Удаляет все данные в индексе Elasticsearch."""
        await es_client.delete_by_query(
            index=INDEX, body={"query": {"match_all": {}}}, conflicts="proceed"
        )

    @staticmethod
    async def _assert_response(response, expected_answer):
        """
        Проверяет статус и тело ответа.

        Параметры:
        - response: словарь с ответом API, содержащий ключи "status" и "body".
        - expected_answer: ожидаемый ответ, включающий ожидаемый статус и тело ответа.

        Проверяет:
        - Соответствие статус-кода.
        - Содержимое поля "detail" или длину тела ответа, если они указаны в expected_answer.
        """
        status, body = response["status"], response["body"]
        assert status == expected_answer["status"]

        if "detail" in expected_answer:
            if body.get("detail") is None:
                for key in expected_answer["detail"]:
                    assert expected_answer["detail"][key] == body[key]
            elif isinstance(body["detail"], list):
                assert expected_answer["detail"]["msg"] == dict(*body["detail"])["msg"]
            else:
                assert expected_answer["detail"] == body["detail"]
        elif "length" in expected_answer:
            assert len(body) == expected_answer["length"]

    @pytest.mark.parametrize(
        ("query_data", "expected_answer"),
        [
            (
                {
                    "genre": "123e4567-e89b-12d3-a456-426614174001",
                    "page_size": 50,
                    "page_number": 1,
                },
                {"status": HTTPStatus.OK, "length": 50},
            ),
            (
                {"genre": 0, "page_size": 50, "page_number": 1},
                {"status": HTTPStatus.NOT_FOUND, "detail": "Фильмы не найдены"},
            ),
        ],
    )
    async def test_film_popular_genre(
        self,
        es_client,
        es_film_data,
        es_write_data,
        make_get_request,
        query_data,
        expected_answer,
    ):
        """Тест получения списка популярных фильмов по жанру."""
        await es_write_data(await es_film_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(FILM_PATH_ROOT, query_data)
            await self._assert_response(response, expected_answer)
            await self.cleaning_es_cache(es_client)

    @pytest.mark.parametrize(
        ("query_data", "expected_answer"),
        [
            (
                {"sort": "invalid", "page_size": 0, "page_number": 0},
                {
                    "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                    "detail": {
                        "msg": [
                            "Input should be '-imdb_rating' or 'imdb_rating'",
                            "Input should be greater than or equal to 1",
                            "Input should be greater than or equal to 1",
                        ]
                    },
                    "reverse": True,
                },
            ),
            (
                {"sort": "-imdb_rating", "page_size": 50, "page_number": 1},
                {"status": HTTPStatus.OK, "reverse": True},
            ),
            (
                {"sort": "imdb_rating", "page_size": 50, "page_number": 1},
                {"status": HTTPStatus.OK, "reverse": False},
            ),
        ],
    )
    async def test_film_popular_genre_sort(
        self,
        es_client,
        es_film_data,
        es_write_data,
        make_get_request,
        query_data,
        expected_answer,
    ):
        """Тест сортировки популярных фильмов по рейтингу."""
        await es_write_data(await es_film_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(FILM_PATH_ROOT, query_data)
            body, status = response["body"], response["status"]

            assert status == expected_answer["status"]

            if status == HTTPStatus.UNPROCESSABLE_ENTITY:
                assert sorted(expected_answer["detail"]["msg"]) == sorted(
                    [detail["msg"] for detail in body["detail"]]
                )
            elif body:
                assert body == sorted(
                    body,
                    key=lambda imdb: imdb["imdb_rating"],
                    reverse=expected_answer["reverse"],
                )

            await self.cleaning_es_cache(es_client)

    @pytest.mark.parametrize(
        ("query_data", "expected_answer"),
        [
            (
                {},
                {
                    "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                    "detail": {"msg": "Field required"},
                },
            ),
            ({"query": "Inception"}, {"status": HTTPStatus.OK, "length": 50}),
            (
                {"query": "Interstellar"},
                {
                    "status": HTTPStatus.NOT_FOUND,
                    "detail": "Фильмы по запросу не найдены.",
                },
            ),
        ],
    )
    async def test_film_search_with_cache(
        self,
        es_client,
        es_film_data,
        make_get_request,
        es_write_data,
        query_data,
        expected_answer,
    ):
        """Тест поиска фильмов по запросу."""
        film_search_path = f"{FILM_PATH_ROOT}/search"
        await es_write_data(await es_film_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(film_search_path, query_data)
            await self._assert_response(response, expected_answer)
            await self.cleaning_es_cache(es_client)

    @pytest.mark.parametrize(
        ("query_data", "expected_answer"),
        [
            (
                {"film_id": str(uuid.uuid4())},
                {"status": HTTPStatus.NOT_FOUND, "detail": "Фильм не найден."},
            ),
            (
                {"film_id": 0},
                {"status": HTTPStatus.OK, "detail": {"id": "0", "title": "Inception"}},
            ),
        ],
    )
    async def test_get_film_with_cache(
        self,
        es_client,
        es_film_data,
        make_get_request,
        es_write_data,
        query_data,
        expected_answer,
    ):
        """Тест получения фильма по его ID."""
        film_id_path = f"{FILM_PATH_ROOT}/{query_data['film_id']}"
        await es_write_data(await es_film_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(film_id_path, query_data)
            await self._assert_response(response, expected_answer)
            await self.cleaning_es_cache(es_client)
