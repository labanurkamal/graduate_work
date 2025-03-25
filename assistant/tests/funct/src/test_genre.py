import uuid
from http import HTTPStatus

import pytest

from funct.settings import test_settings

GENRE_ROOT_PATH = f"{test_settings.service_settings.get_api_v1()}/genres"
INDEX = "genres"
SCHEME = test_settings.es_settings.get_indices_mapping()[INDEX]


@pytest.mark.asyncio
class TestGenre:
    """
    Набор тестов для проверки функциональности обработки запросов к жанрам
    через API. Тесты включают в себя:
    - Проверку списка жанров с использованием кэша.
    - Получение конкретного жанра по его ID с использованием кэша.
    """

    @staticmethod
    async def cleaning_es_cache(es_client):
        """Очистка всех данных в индексе Elasticsearch."""
        await es_client.delete_by_query(
            index=INDEX, body={"query": {"match_all": {}}}, conflicts="proceed"
        )

    @staticmethod
    async def _assert_response(response, expected_answer):
        """
        Сравнение ответа API с ожидаемым результатом.

        Параметры:
        - response: словарь с данными ответа от API, содержащий ключи "status" и "body".
        - expected_answer: ожидаемый результат, включающий ожидаемый статус и тело ответа.

        Метод проверяет:
        - Соответствие статус-кода ответа.
        - Наличие и содержание поля "detail" или длину тела ответа, если это указано в expected_answer.
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
        [({}, {"status": HTTPStatus.OK, "length": 60})],
    )
    async def test_list_genres_with_cache(
        self,
        es_client,
        es_genre_data,
        es_write_data,
        make_get_request,
        query_data,
        expected_answer,
    ):
        """Тест для получения списка жанров с использованием кэша."""
        await es_write_data(await es_genre_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(GENRE_ROOT_PATH, query_data)
            await self._assert_response(response, expected_answer)
            await self.cleaning_es_cache(es_client)

    @pytest.mark.parametrize(
        ("query_data", "expected_answer"),
        [
            (
                {"genre_id": str(uuid.uuid4())},
                {"status": HTTPStatus.NOT_FOUND, "detail": "Жанр не найден."},
            ),
            (
                {"genre_id": 0},
                {"status": HTTPStatus.OK, "detail": {"id": "0", "name": "Drama_0"}},
            ),
        ],
    )
    async def test_get_genre_with_cache(
        self,
        es_client,
        es_genre_data,
        make_get_request,
        es_write_data,
        query_data,
        expected_answer,
    ):
        """Тест для получения жанра по ID с использованием кэша."""
        genre_id_path = f"{GENRE_ROOT_PATH}/{query_data['genre_id']}"
        await es_write_data(await es_genre_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(genre_id_path, query_data)
            await self._assert_response(response, expected_answer)
            await self.cleaning_es_cache(es_client)
