import requests
import time
import uuid
from taskqueue import Producer


producer = Producer("127.0.0.1", "6767")


def run():
    result = requests.get("https://google.co.in")
    print(result.status_code)


for i in range(188):
    producer.enqueue(run)
    time.sleep(1)
