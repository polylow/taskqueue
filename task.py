import uuid

class Task:
	def __init__(self, data):
		self.id = uuid.uuid4().hex
		self.data = data
		self.result = None
