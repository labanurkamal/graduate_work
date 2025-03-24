import uuid
from http import HTTPStatus

import pytest

from funct.settings import test_settings

PERSON_PATH_ROOT = f"{test_settings.service_settings.get_api_v1()}/persons"
INDEX = "persons"
SCHEME = test_settings.es_settings.get_indices_mapping()[INDEX]


@pytest.mark.asyncio
class TestPerson:
    """
    Набор тестов для проверки успешной работы API, связанного с персонажами.
    Тесты включают:
    - Поиск персонажей по имени.
    - Получение информации о конкретном персонаже по его ID.
    - Получение списка фильмов, связанных с персонажем по его ID.
    """

    @staticmethod
    async def cleaning_es_cache(es_client):
        """Удаляет все данные в индексе Elasticsearch."""
        await es_client.delete_by_query(
            index=INDEX, body={"query": {"match_all": {}}}, conflicts="proceed"
        )

    @staticmethod
    async def _assert_response(response, expected_answer):
        """Проверяет статус и тело ответа."""
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
            ({"query": "Leonardo"}, {"status": HTTPStatus.OK, "length": 50}),
            (
                {"query": "Bred Pitt"},
                {"status": HTTPStatus.NOT_FOUND, "detail": "Персонажи не найдены."},
            ),
            (
                {},
                {
                    "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                    "detail": {"msg": "Field required"},
                },
            ),
        ],
    )
    async def test_person_search_with_cache(
        self,
        es_write_data,
        es_person_data,
        es_client,
        make_get_request,
        query_data,
        expected_answer,
    ):
        """Тест поиска персонажей по имени с кэшированием."""
        person_search_path = f"{PERSON_PATH_ROOT}/search"
        await es_write_data(await es_person_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(person_search_path, query_data)
            await self._assert_response(response, expected_answer)
            await self.cleaning_es_cache(es_client)

    @pytest.mark.parametrize(
        ("query_data", "expected_answer"),
        [
            (
                {"person_id": ""},
                {"status": HTTPStatus.NOT_FOUND, "detail": "Not Found"},
            ),
            (
                {"person_id": str(uuid.uuid4())},
                {"status": HTTPStatus.NOT_FOUND, "detail": "Персонаж не найден."},
            ),
            (
                {"person_id": 0},
                {
                    "status": HTTPStatus.OK,
                    "detail": {"id": "0", "full_name": "Leonardo"},
                },
            ),
        ],
    )
    async def test_get_person_with_cache(
        self,
        es_client,
        es_write_data,
        es_person_data,
        make_get_request,
        query_data,
        expected_answer,
    ):
        """Тест получения информации о персонаже по его ID с кэшированием."""
        person_id_path = f"{PERSON_PATH_ROOT}/{query_data['person_id']}"
        await es_write_data(await es_person_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(person_id_path, {})
            await self._assert_response(response, expected_answer)
            await self.cleaning_es_cache(es_client)

    @pytest.mark.parametrize(
        ("query_data", "expected_answer"),
        [
            ({"person_id": 1}, {"status": HTTPStatus.OK, "length": 10}),
            (
                {"person_id": ""},
                {"status": HTTPStatus.NOT_FOUND, "detail": "Not Found"},
            ),
            (
                {"person_id": str(uuid.uuid4())},
                {
                    "status": HTTPStatus.NOT_FOUND,
                    "detail": "Фильмов персонажа не найден.",
                },
            ),
        ],
    )
    async def test_get_person_film_with_cache(
        self,
        es_client,
        es_person_data,
        es_write_data,
        make_get_request,
        query_data,
        expected_answer,
    ):
        """
        Тест получения списка фильмов, связанных с персонажем, по его ID с кэшированием.
        """
        person_id_path = f"{PERSON_PATH_ROOT}/{query_data['person_id']}/film/"
        await es_write_data(await es_person_data(), INDEX, SCHEME)

        for _ in range(2):
            response = await make_get_request(person_id_path, {})
            await self._assert_response(response, expected_answer)
            await self.cleaning_es_cache(es_client)
