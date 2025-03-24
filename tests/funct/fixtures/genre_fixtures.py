import pytest_asyncio


@pytest_asyncio.fixture(name="es_genre_data")
async def es_genre_data():
    """
    Фикстура для создания данных о жанрах для тестирования Elasticsearch.

    Примечание:
        Список содержит 60 записей, каждая из которых представляет отдельный жанр.
    """

    async def inner():
        return [{"id": str(i), "name": f"Drama_{i}"} for i in range(60)]

    return inner
