import asyncio
from collections import defaultdict
from datetime import datetime

import aiofiles
import asyncpg

from core.config import settings, SQL_FILE_ROOT
from models.models import Film, Genre, Person, PersonFilm


class PostgresTransform:
    """
    Класс PostgresTransform отвечает за извлечение данных из PostgreSQL,
    их предварительную обработку и преобразование в модели для загрузки
    в Elasticsearch.
    """

    def __init__(self, pool, modified_time: datetime, batch_size: int = 100):
        self.pool = pool
        self.batch_size = batch_size
        self.modified_time = modified_time

    @staticmethod
    async def read_sql_file(filepath: str) -> str:
        """Читает SQL-запрос из файла."""
        async with aiofiles.open(SQL_FILE_ROOT + filepath, mode="r") as file:
            sql_query = await file.read()

        return sql_query

    async def fetch_with_cursor(self, sql_command: str, params: tuple) -> list:
        """Извлекает данные из PostgreSQL, используя курсор."""
        results = []
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                cursor = await conn.cursor(sql_command, *params)

                while True:
                    data = await cursor.fetch(self.batch_size)
                    if not data:
                        break
                    results.extend(data)
        return results

    async def load_genre(self) -> list:
        """Извлекает данные о жанрах из PostgreSQL."""
        sql_query = await self.read_sql_file("genre.sql")
        return await self.fetch_with_cursor(sql_query, (self.modified_time,))

    async def load_person(self) -> list:
        """Извлекает данные о людях из PostgreSQL."""
        sql_query = await self.read_sql_file("person.sql")
        return await self.fetch_with_cursor(sql_query, (self.modified_time,))

    async def load_person_film_work(self) -> list:
        """Извлекает данные о связях между людьми и фильмами из PostgreSQL."""
        sql_query = await self.read_sql_file("person_film_work.sql")
        return await self.fetch_with_cursor(sql_query, (self.modified_time,))

    async def load_movie(self, persons: list) -> list:
        """Извлекает данные о фильмах на основе списка лиц."""
        persons_idx = [person.id for person in persons]
        sql_query = await self.read_sql_file("movie.sql")

        return await self.fetch_with_cursor(
            sql_query, (self.modified_time, persons_idx)
        )

    @staticmethod
    async def identify_person_film(data: list) -> list:
        """Группирует данные о лицах и их фильмах."""
        grouped_data = defaultdict(lambda: {"full_name": None, "films": []})

        for record in data:
            person_id = record["id"]
            grouped_data[person_id]["full_name"] = record["full_name"]
            grouped_data[person_id]["films"].append(
                {
                    "id": record["film_work_id"],
                    "title": record["title"],
                    "imdb_rating": record["imdb_rating"],
                    "roles": record["roles"].split(", "),
                }
            )

        return [
            {"id": person_id, **details} for person_id, details in grouped_data.items()
        ]

    async def fetch_person_film_work_from_postgres(self) -> list:
        """Извлекает и преобразует данные о связях лиц и фильмов из PostgreSQL."""
        load_person_film_work = await self.load_person_film_work()
        return [
            PersonFilm(**item)
            for item in await self.identify_person_film(load_person_film_work)
        ]

    async def fetch_genre_from_postgres(self) -> list:
        """Извлекает и преобразует данные о жанрах из PostgreSQL."""
        load_genre = await self.load_genre()
        return [Genre(id=genre["id"], name=genre["name"]) for genre in load_genre]

    async def fetch_person_from_postgres(self) -> list:
        """Извлекает и преобразует данные о людях из PostgreSQL."""
        load_person = await self.load_person()
        return [
            Person(id=person["id"], full_name=person["full_name"])
            for person in load_person
        ]

    async def fetch_movie_from_postgres(self) -> list:
        """Извлекает и преобразует данные о фильмах из PostgreSQL."""
        load_movie = await self.load_movie(await self.fetch_person_from_postgres())
        film = []
        for movie in load_movie:
            role_person = await self.identify_person_role(movie)
            genres = await self.identify_genre(movie)
            film.append(
                Film(
                    id=movie["film_work_id"],
                    title=movie["title"],
                    imdb_rating=movie["imdb_rating"],
                    description=movie["description"],
                    genre=genres,
                    actors=role_person["actor"],
                    writers=role_person["writer"],
                    directors=role_person["director"],
                )
            )

        return film

    @staticmethod
    async def identify_genre(movie: dict) -> list:
        """Извлекает жанры из данных фильма."""
        genres = []
        for item in movie["genres"].split(", "):
            genre_id, genre_name = item.split(":")
            genres.append(Genre(id=genre_id, name=genre_name))

        return genres

    @staticmethod
    async def zip_person_data(movie: dict):
        """Объединяет данные о лицах и ролях."""
        person_ids = movie["person_ids"].split(", ")

        persons_with_roles = [
            item.split(":") for item in movie["persons_with_roles"].split(", ")
        ]
        return zip(person_ids, persons_with_roles)

    async def identify_person_role(self, movie: dict) -> dict:
        """Извлекает роли лиц из данных фильма."""
        roles = {"writer": [], "actor": [], "director": []}

        zip_person_data = await self.zip_person_data(movie)

        for person_id, name_role in zip_person_data:
            full_name, role = name_role
            if role in roles:
                roles[role].append(Person(id=person_id, full_name=full_name))

        return roles


async def handler_et_process() -> zip:
    """
    Основной процесс ETL для извлечения данных из PostgreSQL и их подготовки
    для дальнейшей загрузки в Elasticsearch.
    """
    modified_time = datetime.strptime("1978.04.03", "%Y.%m.%d")

    pool = await asyncpg.create_pool(settings.postgres_url)

    try:
        data = PostgresTransform(pool, modified_time=modified_time, batch_size=100)

        postgres_data_tasks = {
            "genres": asyncio.create_task(data.fetch_genre_from_postgres()),
            "persons": asyncio.create_task(data.fetch_person_film_work_from_postgres()),
            "movies": asyncio.create_task(data.fetch_movie_from_postgres()),
        }
        results = await asyncio.gather(*postgres_data_tasks.values())

        return zip(postgres_data_tasks.keys(), results)

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(handler_et_process())
