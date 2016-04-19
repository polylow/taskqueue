import requests
import time
from taskqueue import Producer


producer = Producer()


def run():
    result = requests.get("https://google.co.in")
    print(result.status_code)


for i in range(188):
    producer.enqueue(run)
    time.sleep(1)
