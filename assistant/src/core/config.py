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


class AssistantSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env"), env_file_encoding="utf-8", extra="ignore"
    )
    card_title: str = Field(..., alias="CARD_TITLE")
    card_description: str = Field(..., alias="CARD_DISCRIPTION")
    card_image_id: str = Field(..., alias="CARD_IMAGE_ID")


settings = Settings()
assistant_settings = AssistantSettings()

ELASTIC_SCHEMES_PATH = BASE_DIR + "/etl/schema"
SQL_FILE_ROOT = BASE_DIR + "/etl/queries/"

INTENT_MODEL_PATH = BASE_DIR + "/output/intent/output_intent/model-best"
ENTITY_MODEL_PATH = BASE_DIR + "/output/ner/model-best"
