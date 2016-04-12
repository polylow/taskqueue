import redis
import queue
import thriftpy


redis_ip = "127.0.0.1"
redis_port = 6767
master_ip = "172.16.1.146"
master_port = 9090

tq = queue.Queue()  # queue of task objs

producers = []
workers = []
threads = []


class Worker:

    def __init__(self, ip, port):
        self.r = redis.Redis(host=redis_ip, port=redis_port)
        # self.id = None
        self.ip = ip
        self.port = port

    def set_available(self):
        self.r.set(self.id+".available", "1")

    def set_not_available(self):
        self.r.set(self.id+".available", "0")

    def is_available(self):
        if self.r.get(self.id+".available") == 0:
            return False
        else:
            return True

    def task_service(self, task):
        task = marshal.loads(task)
        work(task)

    def work(self, task):
        self.r.set(task.id, "running")
        result = None
        try:
            run = types.FunctionType(task.data, globals(), "run")
            result = run()
            self.r.set(task.id, "finished")
        except Exception:
            self.r.set(task.id, "failed")
        return result
