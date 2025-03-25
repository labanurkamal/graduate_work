from dependency_injector import containers, providers
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from core.config import Settings
from dependencies.register import RepositoryFactory
from services.cache import RedisCacheRepository
from services.film import FilmService
from services.genre import GenreService
from services.person import PersonService
from services.storage import ElasticStorageRepository
from services.assistant import IntentNERModel, AssistantService


class CoreContainer(containers.DeclarativeContainer):
    """Предоставляет основные ресурсы, такие как клиенты Redis и Elasticsearch, а также экземпляры репозиториев."""

    config = providers.Singleton(Settings)
    redis_client = providers.Singleton(
        Redis,
        host=config.provided.redis_host,
        port=config.provided.redis_port,
        password=config.provided.redis_password,
    )
    elastic_client = providers.Singleton(
        AsyncElasticsearch, hosts=config.provided.elastic_url
    )
    cache = providers.Singleton(RedisCacheRepository, cache=redis_client)
    storage = providers.Singleton(ElasticStorageRepository, storage=elastic_client)


class ServiceContainer(containers.DeclarativeContainer):
    """Предоставляет сервисы приложения (FilmService, GenreService, PersonService) с необходимыми зависимостями."""

    repository_factory = providers.Factory(
        RepositoryFactory,
        cache=CoreContainer.cache,
        storage=CoreContainer.storage,
    )

    film_service = providers.Factory(FilmService, repository=repository_factory)
    genre_service = providers.Factory(GenreService, repository=repository_factory)
    person_service = providers.Factory(PersonService, repository=repository_factory)
    intent_ner_model = providers.Singleton(IntentNERModel)
    assistant_service = providers.Singleton(
        AssistantService,
        film_service=film_service,
        person_service=person_service,
        intent_ner_model=intent_ner_model,
    )
