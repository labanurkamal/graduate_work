import logging

import backoff
from elasticsearch import ConnectionError, Elasticsearch

from assistant.tests.funct.settings import test_settings


@backoff.on_exception(backoff.expo, ConnectionError, max_time=90)
def wait_for_es():
    es_client = Elasticsearch(hosts=[test_settings.es_settings.get_url()])

    if es_client.ping():
        logging.info("Elasticsearch доступен.")
    else:
        logging.warning("Elasticsearch недоступен. Пробуем снова...")
        raise ConnectionError("Elasticsearch недоступен.")


if __name__ == "__main__":
    try:
        wait_for_es()
    except ConnectionError as e:
        logging.error(
            f"Elasticsearch недоступен после всех попыток. Возникающий ошибка {e}"
        )
