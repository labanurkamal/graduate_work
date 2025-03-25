from typing import Optional

from pydantic import BaseModel, Field, confloat

from models.models import Person


class UUIDMixin(BaseModel):
    """Миксин для добавления UUID в качестве поля `id` с генерацией уникального идентификатора по умолчанию."""

    id: str


class ShortFilm(UUIDMixin):
    """Модель для краткой информации о фильме."""

    title: str
    imdb_rating: Optional[confloat(ge=1, le=10)]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Inception",
                "imdb_rating": 8.8,
            }
        }


class FilmRole(UUIDMixin):
    """Модель для информации о ролях в фильме."""

    roles: list[str] = Field(default_factory=list)


class PersonFilm(Person):
    """Модель для информации о человеке и его ролях в фильмах."""

    films: list[FilmRole] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "full_name": "Leonardo DiCaprio",
                "films": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174006",
                        "roles": ["actor"],
                    },
                ],
            }
        }
