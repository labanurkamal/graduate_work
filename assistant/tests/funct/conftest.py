import asyncio

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.funct.settings import test_settings

pytest_plugins = (
    "tests.funct.fixtures.film_fixtures",
    "tests.funct.fixtures.genre_fixtures",
    "tests.funct.fixtures.person_fixtures",
)


ES_HOSTS = test_settings.es_settings.get_url()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Создает и предоставляет асинхронный event loop на уровне всей сессии тестирования.
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="client_session", scope="session")
async def client_session():
    """Создает сессию aiohttp для HTTP-запросов."""
    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        yield session


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client():
    """
    Создает асинхронного клиента Elasticsearch для выполнения запросов к Elasticsearch.
    """
    es_client = AsyncElasticsearch(hosts=ES_HOSTS, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name="es_write_data")
async def es_write_data(es_client):
    """
    Фикстура для записи данных в Elasticsearch.

    Создает индекс в Elasticsearch с заданной схемой и записывает предоставленные данные.
    Выполняет проверку, существует ли индекс, и обновляет его.
    """

    async def inner(es_data: list[dict], index_name: str, schema):
        bulk_query = [
            {"_index": index_name, "_id": row["id"], "_source": row} for row in es_data
        ]
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(index=index_name, body=schema)

        updated, errors = await async_bulk(es_client, actions=bulk_query)
        await es_client.indices.refresh(index=index_name)

        if errors:
            raise Exception("Ошибка записи данных в Elasticsearch")

    return inner


@pytest_asyncio.fixture(name="make_get_request")
async def make_get_request(client_session):
    """
    Фикстура для выполнения GET-запросов к API с указанными параметрами.
    """

    async def inner(path: str, query):
        async with client_session.get(path, params=query) as response:
            return {
                "status": response.status,
                "body": await response.json(),
                "headers": response.headers,
            }

    return inner
