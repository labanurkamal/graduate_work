import pytest_asyncio


@pytest_asyncio.fixture(name="es_film_data")
async def es_film_data():
    """
    Фикстура для генерации тестовых данных о фильмах для Elasticsearch.

    Примечание:
        Список содержит 60 записей, каждый с уникальным `id` и рейтингом IMDb, который постепенно уменьшается.
    """

    async def inner():
        return [
            {
                "id": str(i),
                "title": "Inception",
                "imdb_rating": round((9.8 - i / 10), 2),
                "description": "A mind-bending thriller about dream manipulation.",
                "genre": [
                    {"id": "123e4567-e89b-12d3-a456-426614174001", "name": "Action"}
                ],
                "actors": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "full_name": "Leonardo DiCaprio",
                    }
                ],
                "writers": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174004",
                        "full_name": "Christopher Nolan",
                    }
                ],
                "directors": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174005",
                        "full_name": "Christopher Nolan",
                    }
                ],
            }
            for i in range(60)
        ]

    return inner
