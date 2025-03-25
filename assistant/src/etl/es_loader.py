import asyncio
import json
import logging
import os

import aiofiles
from elasticsearch import AsyncElasticsearch, helpers

from core.config import ELASTIC_SCHEMES_PATH
from etl.handler_et import handler_et_process


class ElasticsearchLoader:
    """
    Класс для загрузки данных в Elasticsearch, включающий проверку, создание
    индексов и массовую отправку данных.

    Методы:
        load_data(index_name, data): Подготавливает данные и отправляет их
        в Elasticsearch с использованием bulk API.
        async_bulk_index(es, actions): Выполняет массовую загрузку данных в Elasticsearch.
        indices_exists(index_name): Проверяет, существует ли индекс в Elasticsearch.
        create_index(index_name, schema): Создаёт индекс в Elasticsearch с заданной схемой.
        get_schema(schema_path): Получает схему индекса из указанного файла.
    """

    def __init__(self, es: AsyncElasticsearch):
        self.es = es

    async def load_data(self, index_name, data):
        """Подготавливает данные и отправляет их в Elasticsearch с использованием bulk API."""
        actions = [
            {"_index": index_name, "_id": item.id, "_source": item.model_dump()}
            for item in data
        ]

        try:
            await self.async_bulk_index(self.es, actions)
            logging.info(f"Успешно {len(actions)} данных отправлены в Elasticsearch")
        except Exception as e:
            logging.error(f"Ошибка при отправке данных в Elasticsearch: {e}")
            raise

    @staticmethod
    async def async_bulk_index(es, actions):
        """Асинхронная массовая загрузка данных в Elasticsearch с использованием хелпера async_bulk."""
        await helpers.async_bulk(es, actions)

    async def indices_exists(self, index_name) -> bool:
        """Проверяет существование индекса в Elasticsearch."""
        return await self.es.indices.exists(index=index_name)

    async def create_index(self, index_name, schema) -> None:
        """Создаёт индекс в Elasticsearch с заданной схемой, если он не существует."""
        try:
            if await self.indices_exists(index_name):
                logging.info(f"Индекс {index_name} уже существует.")
            else:
                logging.info(f"Создаем индекс {index_name} с заданной схемой.")
                await self.es.indices.create(index=index_name, body=schema)
                logging.info(f"Индекс {index_name} успешно создан.")
        except Exception as e:
            logging.error(f"Ошибка при создании индекса {index_name}: {e}")
            raise

    @staticmethod
    async def get_schema(schema_path: str):
        """Получает схему индекса из файла."""
        file_name = schema_path.split("/")[-1]
        try:
            async with aiofiles.open(schema_path, "r") as file:
                schema = json.loads(await file.read())
            logging.info(f"Схема была успешно получена из файла {file_name}")
            return schema
        except FileNotFoundError:
            logging.error(f"Файл {file_name} не найден.")
            raise
        except json.JSONDecodeError:
            logging.error(f"Ошибка при чтении файла {file_name}: некорректный JSON.")
            raise


async def load_data_to_elasticsearch(es_conn):
    """Загружает схемы индексов и данные в Elasticsearch.

    Осуществляет:
    1. Загрузку всех схем из файлов, содержащихся в директории.
    2. Проверку и создание недостающих индексов на основе загруженных схем.
    3. Получение обработанных данных из ETL процесса.
    4. Асинхронную загрузку данных в соответствующие индексы.
    """
    directory_path = ELASTIC_SCHEMES_PATH

    es = ElasticsearchLoader(es_conn)
    for file_path in os.listdir(directory_path):
        file_name = file_path.split(".")[0]
        schema = await es.get_schema(os.path.join(directory_path, file_path))
        await es.create_index(file_name, schema)

    results = await handler_et_process()

    elastic_tasks = [
        asyncio.create_task(es.load_data(index_name, data))
        for index_name, data in results
    ]

    await asyncio.gather(*elastic_tasks)
