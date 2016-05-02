import requests
import time
import uuid
from taskqueue import Producer


producer = Producer()


def run():
    raise Exception


for i in range(188):
    producer.enqueue(run)
    time.sleep(2)
