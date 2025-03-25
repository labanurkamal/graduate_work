import json
import os
from logging import config as logging_conf

from dotenv import find_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .utils.logger import LOGGING

logging_conf.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ServiceSettings(BaseSettings):
    """
    Конфигурация для настроек FastAPI-приложения.

    Атрибуты:
        host (str): Хост для запуска FastAPI.
        port (str): Порт для запуска FastAPI.

    Методы:
        get_url() -> str: Возвращает полный URL для FastAPI.
        get_api_v1() -> str: Возвращает путь к API версии 1.
    """

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env.test"),
        env_prefix="fastapi_",
        extra="ignore",
    )
    host: str = ...
    port: str = ...

    def get_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def get_api_v1(self):
        return f"{self.get_url()}/api/v1"


class ElasticsearchSettings(BaseSettings):
    """
    Конфигурация для настроек Elasticsearch.

    Атрибуты:
        host (str): Хост для подключения к Elasticsearch.
        port (str): Порт для подключения к Elasticsearch.
        indices (str): Список индексов, разделённых запятыми.
        indices_mapping (str): Путь к JSON-файлам с маппингами индексов.

    Методы:
        validate_indices(indices: str) -> list[str]: Валидирует индексы, разделяя их по запятым.
        get_mapping(index: str) -> dict: Загружает маппинг для указанного индекса из JSON-файла.
        get_indices_mapping() -> dict[str, dict]: Возвращает маппинги всех индексов.
        get_url() -> str: Возвращает URL для подключения к Elasticsearch.
    """

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env.test"), env_prefix="es_", extra="ignore"
    )
    host: str = ...
    port: str = ...
    indices: str = ...
    indices_mapping: str = ...

    @field_validator("indices")
    def validate_indices(cls, indices: str) -> list[str]:
        return indices.split(",")

    def get_mapping(self, index: str):
        mapping_file = f"{BASE_DIR}{self.indices_mapping}{index}_mapping.json"
        with open(mapping_file, "r") as file:
            return json.load(file)

    def get_indices_mapping(self) -> dict[str, dict]:
        indices_mappings = {}
        for index in self.indices:
            indices_mappings[index] = self.get_mapping(index)
        return indices_mappings

    def get_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def elastic_url(self):
        return f"http://{self.host}:{self.port}"


class RedisSettings(BaseSettings):
    """
    Конфигурация для настроек Redis.

    Атрибуты:
        host (str): Хост для подключения к Redis.
        port (str): Порт для подключения к Redis.
        password (str): Пароль для подключения к Redis.
    """

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env.test"), env_prefix="redis_", extra="ignore"
    )
    host: str = ...
    port: str = ...
    password: str = ...


class TestSettings(BaseSettings):
    """
    Основные настройки тестовой среды, включающие настройки FastAPI, Elasticsearch и Redis.

    Атрибуты:
        fastapi_settings (FastapiSettings): Настройки FastAPI.
        es_settings (ElasticsearchSettings): Настройки Elasticsearch.
        redis_settings (RedisSettings): Настройки Redis.
    """

    service_settings: ServiceSettings = ServiceSettings()
    es_settings: ElasticsearchSettings = ElasticsearchSettings()
    redis_settings: RedisSettings = RedisSettings()


test_settings = TestSettings()
