import requests
import time
import uuid
from taskqueue import Producer


producer = Producer()


def run():
    result = requests.get("http://ayushshanker.me")
    print(result.status_code)


for i in range(188):
    producer.enqueue(run)
    time.sleep(2)
