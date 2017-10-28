import requests
import time
import logging

from taskqueue import Producer

logger = logging.getLogger(__name__)
producer = Producer()


def run():
    result = requests.get("https://google.co.in")
    logger.info(result.status_code)


for i in range(188):
    producer.enqueue(run)
    time.sleep(1)
