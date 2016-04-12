import requests
import time
import uuid
from taskqueue import Producer

def run():
	result = requests.get("https://google.co.in")
	print(result.status_code)

producer_uuid = uuid.uuid4.hex[:6]
producer = Producer(producer_uuid, "127.0.0.1", "6767")

for i in range(188):
	producer.enqueue(run)
	time.sleep(1)
