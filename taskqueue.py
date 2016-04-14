import sys
import uuid
import redis
import queue
from hashlib import md5
import threading
import dill, types
from task import Task
from hashlib import md5
import pudb as pdb
import requests

import thriftpy
rpc_thrift = thriftpy.load('rpc.thrift', module_name='rpc_thrift')
from thriftpy.rpc import make_server, make_client

redis_ip = '127.0.0.1'
redis_port = 6379
master_ip = '172.16.1.137'
master_port = 9091

tq = queue.Queue()  # queue of task objs
pending_queue = {}
workers = []
threads = []


def send(task, ip, port):
    # pdb.set_trace()
    client = make_client(rpc_thrift.RPC, ip, port)
    client.task_service(task)


class Producer:

    def __init__(self, ip, port):
        self.r = redis.Redis(host=redis_ip, port=redis_port)
        self.available = False

    def set_available(self):
        self.available = True

    def set_not_available(self):
        self.available = False

    def enqueue(self, work):
        source = work.__code__
        task = Task(source)
        data = dill.dumps(task)
        self.r.set(task.id, 'pending')
        send(data, master_ip, master_port)


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
        task = dill.loads(task)
        self.work(task)

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


def add_producer(ip, port):
    producer_id = md5(ip+port).hexdigest[:6]
    producer = Producer(producer_id, redis_ip, redis_port)
    producer.available = True
    producers.push(producer)


def add_worker(ip, port):
    worker_id = md5(ip+port).hexdigest[:8]
    worker = Worker(worker_id, ip, port)
    worker.available = True
    workers.push(worker)


def round_robin():
    offset = 0
    while True:
        if workers[offset].is_available():
            worker = workers[offset]
            task = tq.get()
            send(task, worker.ip, worker.port)
        offset += 1
        offset = offset % len(workers)


class QueueHandler:
    def __init__(self):
        pass

    def task_service(self, task):
        # task = marshal.loads(task)
        tq.put(task)



def listen():
    server = make_server(rpc_thrift.RPC, QueueHandler(), master_ip, master_port)
    server.serve()

def main():
    add_worker('172.16.0.170', 9091)
    round_robin()


# Threading
if __name__ == '__main__':
    main_thread = threading.Thread(target=main)
    threads.append(main_thread)
    main_thread.start()

    listener_thread = threading.Thread(target=listen)
    threads.append(listener_thread)
    listener_thread.start()
