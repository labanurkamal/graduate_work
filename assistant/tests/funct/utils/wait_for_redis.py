import logging

import backoff
from redis import ConnectionError, Redis

from assistant.tests.funct.settings import test_settings


@backoff.on_exception(backoff.expo, ConnectionError, max_time=90)
def wait_for_redis():
    redis_client = Redis(
        host=test_settings.redis_settings.host,
        port=test_settings.redis_settings.port,
        password=test_settings.redis_settings.password,
    )

    if redis_client.ping():
        logging.info("Redis доступен.")
    else:
        logging.warning("Redis недоступен. Пробуем снова...")
        raise ConnectionError("Redis недоступен")


if __name__ == "__main__":
    try:
        wait_for_redis()
    except ConnectionError:
        logging.error("Redis недоступен после всех попыток.")
