import uuid
import time

class Task:
	def __init__(self, data):
		self.id = uuid.uuid4().hex
		self.data = data
		self.result = None
		self.creation_time = time.time()
		self.running_time = None
