import logging
from typing import Any, Union

import spacy
from schemas.assistant_schema import IntentFields, EntityType, IntentHandlers

from services.film import FilmService
from services.person import PersonService
from core.config import INTENT_MODEL_PATH, ENTITY_MODEL_PATH


class IntentNERModel:
    def __init__(self) -> None:
        self.intent_nlp = spacy.load(INTENT_MODEL_PATH)
        self.ner_nlp = spacy.load(ENTITY_MODEL_PATH)

    def model_intent(self, text: str) -> str:
        doc = self.intent_nlp(text)
        scores = {k: v for k, v in doc.cats.items()}
        predicted_category = max(scores.items(), key=lambda x: x[1])[0]
        return predicted_category

    def model_entities(self, text: str) -> dict[str, EntityType]:
        doc = self.ner_nlp(text)
        entities = {ent.text: ent.label_ for ent in doc.ents}

        return entities


class AssistantService:
    def __init__(
        self,
        film_service: FilmService,
        person_service: PersonService,
        intent_ner_model: IntentNERModel,
    ) -> None:
        self.film_service = film_service
        self.person_service = person_service
        self.intent_ner_model = intent_ner_model

    async def handle_request(self, entities: dict[str, EntityType], intent: str) -> str:
        entity_name, entity_type = next(iter(entities.items()))
        es_query = await self.es_query(query=entity_name, entity_type=entity_type)
        logging.info(f'Запрос для Elasticsearch: {es_query}')
        response = await self.get_response(entity_name, entity_type, es_query, intent)

        return response

    async def get_response(self, entity_name: str, entity_type: EntityType, es_query: dict[str, Any], intent: str) -> str:
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
                attr = next((a for a in ["title", "full_name"] if hasattr(value[0], a)), None)
                value = ", ".join([getattr(v, attr, str(v)) for v in value]) if attr else ", ".join(map(str, value))

            results.append(str(value))

        return response_template.format(response=", ".join(results), entity_name=entity_name)


    async def define_service(self, entity_type) -> Union[FilmService, PersonService]:
        if entity_type == EntityType.PERSON:
            return self.person_service
        elif entity_type == EntityType.FILM:
            return self.film_service
        else:
            raise ValueError(f"Неизвестный тип сущности: {entity_type}")

    @staticmethod
    async def es_query(query: str, entity_type: EntityType) -> dict[str, Any]:
        fields_map = {EntityType.PERSON: ["full_name"], EntityType.FILM: ["title"]}
        return {"query": {"multi_match": {"query": query, "fields": fields_map.get(entity_type, [])}}}


    async def process_request(self, text: str) -> str:
        entities = self.intent_ner_model.model_entities(text)
        intent = self.intent_ner_model.model_intent(text)

        if not (entities and intent):
            return "Извините, я не понимаю, вы можете задать вопрос еще раз."

        log_e = tuple(*entities.items())
        logging.info(f'1. Сущность: {entities}, Намериние: {intent}')
        logging.info(f'2. Имя: {log_e[0]}. Относиться: {log_e[1]}. Что нужно от {log_e[1]} нужно {intent}')
        return await self.handle_request(entities, intent)
