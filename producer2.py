import time
from taskqueue import Producer


producer = Producer()


def run():
    raise Exception


for _ in range(188):
    producer.enqueue(run)
    time.sleep(2)
