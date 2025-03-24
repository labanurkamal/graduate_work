from typing import Optional

from pydantic import BaseModel, Field, confloat


class UUIDMixin(BaseModel):
    """Миксин для добавления UUID в качестве поля `id` с генерацией уникального идентификатора по умолчанию."""

    id: str


class Genre(UUIDMixin):
    """Модель для информации о жанре фильма."""

    name: str = Field(max_length=255)

    class Config:
        json_schema_extra = {
            "example": {"id": "123e4567-e89b-12d3-a456-426614174001", "name": "Action"}
        }


class Person(UUIDMixin):
    """Модель для информации о человеке."""

    full_name: str = Field(max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "full_name": "Leonardo DiCaprio",
            }
        }


class Film(UUIDMixin):
    """Модель для информации о фильме."""

    title: str
    imdb_rating: Optional[confloat(ge=1.0, le=10.0)]
    description: Optional[str] = None
    genre: list[Genre] = Field(default_factory=list)
    actors: list[Person] = Field(default_factory=list)
    writers: list[Person] = Field(default_factory=list)
    directors: list[Person] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "title": "Inception",
                "imdb_rating": 8.8,
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
        }


class FilmRole(UUIDMixin):
    """Модель для информации о ролях, названиях и рейтинге в фильме."""

    title: str
    imdb_rating: Optional[confloat(ge=1.0, le=10.0)]
    roles: list[str] = Field(default_factory=list)


class PersonFilm(Person):
    """Модель для информации о человеке и его ролях в фильмах."""

    films: list[FilmRole] = Field(default_factory=list)
