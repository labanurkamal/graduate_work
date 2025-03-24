import os
from logging import config as logging_config

from dotenv import find_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env"), env_file_encoding="utf-8", extra="ignore"
    )
    project_name: str = Field(..., alias="PROJECT_NAME")
    postgres_url: str = Field(..., alias="POSTGRES_URL")
    redis_host: str = Field(..., alias="REDIS_HOST")
    redis_port: str = Field(..., alias="REDIS_PORT")
    redis_password: str = Field(..., alias="REDIS_PASSWORD")
    redis_url: str = Field(..., alias="REDIS_URL")
    elastic_url: str = Field(..., alias="ELASTIC_URL")
    elastic_schemes_path: str = Field(..., alias="ELASTIC_SCHEMES_PATH")
    sql_file_root: str = Field(..., alias="SQL_SOURCE_ROOT")

class AssistantSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env"), env_file_encoding="utf-8", extra="ignore"
    )
    intent_path: str = Field(..., alias="INTENT_PATH")
    entity_path: str = Field(..., alias="ENTITY_PATH")


settings = Settings()
assistant_settings = AssistantSettings()

ELASTIC_SCHEMES_PATH = BASE_DIR + settings.elastic_schemes_path
SQL_FILE_ROOT = BASE_DIR + settings.sql_file_root

INTENT_MODEL_PATH = BASE_DIR + assistant_settings.intent_path
ENTITY_MODEL_PATH = BASE_DIR + assistant_settings.entity_path