import logging
from typing import Any, Union

import spacy

from core.config import ENTITY_MODEL_PATH, INTENT_MODEL_PATH
from schemas.assistant_schema import EntityType, IntentFields, IntentHandlers
from services.film import FilmService
from services.person import PersonService


class IntentNERModel:
    """Класс для обработки текста с помощью моделей определения намерений и извлечения сущностей."""

    def __init__(self) -> None:
        """Загружает предобученные модели для классификации намерений и извлечения сущностей."""
        self.intent_nlp = spacy.load(INTENT_MODEL_PATH)
        self.ner_nlp = spacy.load(ENTITY_MODEL_PATH)

    def model_intent(self, text: str) -> str:
        """Определяет намерение пользователя на основе текста."""
        doc = self.intent_nlp(text)
        scores = {k: v for k, v in doc.cats.items()}
        predicted_category = max(scores.items(), key=lambda x: x[1])[0]
        return predicted_category

    def model_entities(self, text: str) -> dict[str, EntityType]:
        """Извлекает сущности (персоны, фильмы) из текста пользователя."""
        doc = self.ner_nlp(text)
        entities = {ent.text: ent.label_ for ent in doc.ents}
        return entities


class AssistantService:
    """Сервис обработки запросов пользователя и формирования ответов."""

    def __init__(
            self,
            film_service: FilmService,
            person_service: PersonService,
            intent_ner_model: IntentNERModel,
    ) -> None:
        """Инициализирует сервис с доступом к данным о фильмах и персонажах."""
        self.film_service = film_service
        self.person_service = person_service
        self.intent_ner_model = intent_ner_model

    async def handle_request(self, entities: dict[str, EntityType], intent: str) -> str:
        """Обрабатывает запрос, формирует поисковый запрос и получает ответ."""
        entity_name, entity_type = next(iter(entities.items()))
        es_query = await self.es_query(query=entity_name, entity_type=entity_type)
        logging.info(f"Запрос для Elasticsearch: {es_query}")
        response = await self.get_response(entity_name, entity_type, es_query, intent)
        return response

    async def get_response(
            self,
            entity_name: str,
            entity_type: EntityType,
            es_query: dict[str, Any],
            intent: str,
    ) -> str:
        """Формирует ответ на основе результатов поиска и шаблона намерения."""
        service = await self.define_service(entity_type)
        search = await service.get_by_search(es_query)
        response_template = IntentHandlers[intent].value
        intent_field = IntentFields[intent].value

        if not search:
            return f"Данные о {'фильме' if entity_type == EntityType.FILM else 'персоне'} {entity_name} не найдены."

        results = []
        for item in search:
            value = getattr(item, intent_field, "Нет данных")
            logging.info(f"VALUE: {value}")

            if isinstance(value, list) and value:
                attr = next(
                    (a for a in ["title", "full_name"] if hasattr(value[0], a)), None
                )
                value = (
                    ", ".join([getattr(v, attr, str(v)) for v in value])
                    if attr
                    else ", ".join(map(str, value))
                )

            results.append(str(value))

        return response_template.format(
            response=", ".join(results), entity_name=entity_name
        )

    async def define_service(self, entity_type) -> Union[FilmService, PersonService]:
        """Определяет, к какому сервису обращаться (фильмы или персоны)."""
        if entity_type == EntityType.PERSON:
            return self.person_service
        elif entity_type == EntityType.FILM:
            return self.film_service

    @staticmethod
    async def es_query(query: str, entity_type: EntityType) -> dict[str, Any]:
        """Формирует поисковый запрос для Elasticsearch."""
        fields_map = {EntityType.PERSON: ["full_name"], EntityType.FILM: ["title"]}
        return {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": fields_map.get(entity_type, []),
                }
            }
        }

    async def process_request(self, text: str) -> str:
        """Анализирует текст запроса, извлекает сущности, определяет намерение и формирует ответ."""
        entities = self.intent_ner_model.model_entities(text)
        intent = self.intent_ner_model.model_intent(text)

        if not (entities and intent):
            return "Извините, я не понимаю, вы можете задать вопрос еще раз."

        log_e = tuple(*entities.items())
        logging.info(f"1. Сущность: {entities}, Намерение: {intent}")
        logging.info(
            f"2. Имя: {log_e[0]}. Относится: {log_e[1]}. Что нужно от {log_e[1]}: {intent}"
        )
        return await self.handle_request(entities, intent)
