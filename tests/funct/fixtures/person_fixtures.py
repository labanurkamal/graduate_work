import pytest_asyncio


@pytest_asyncio.fixture(name="es_person_data")
async def es_person_data():
    """
    Фикстура для создания данных о персонажах для тестирования Elasticsearch.

    Примечание:
        Список содержит 60 записей, каждая из которых представляет отдельного персонажа с одинаковым именем и фильмами.
    """

    async def inner():
        return [
            {
                "id": str(i),
                "full_name": "Leonardo",
                "films": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174006",
                        "title": "Inception",
                        "imdb_rating": 10,
                        "roles": ["actor"],
                    }
                ]
                * 10,
            }
            for i in range(60)
        ]

    return inner
