import sys
import types
import queue
import threading
import logging
from time import time
from hashlib import md5
import dill
import redis
from task import Task

import thriftpy
from thriftpy.rpc import make_server, make_client

logger = logging.getLogger(__name__)

dequeue_thrift = thriftpy.load('dequeue.thrift', module_name='dequeue_thrift')
enqueue_thrift = thriftpy.load('enqueue.thrift', module_name='enqueue_thrift')


def get_ip(interface='eth0'):
    from netifaces import AF_INET
    import netifaces as ni
    return ni.ifaddresses(interface)[AF_INET][0]['addr']

redis_ip = "127.0.0.1"
redis_port = 6379
master_ip = "127.0.0.1"
master_port = 9091
rconn = redis.Redis(redis_ip, redis_port)
tq = queue.Queue()  # queue of task objs
tasks = {}
workers = []
threads = []


def top_n(tqueue, n):
    result = []
    iterable = tqueue.__iter__()
    for _ in range(n):
        try:
            result.append(next(iterable))
        except StopIteration:
            break
    return result


def top_pending(n):
    return top_n(tq, 5)


def last_running():
    result = []
    for worker in workers:
        result.append(getstr('worker:' + worker.id + '.current'))
    none_count = result.count(None)
    return filter(lambda x: x is not None, result)


def getint(id):
    try:
        return int(rconn.get(id).decode('utf-8'))
    except AttributeError:
        return None


def getstr(id):
    try:
        return rconn.get(id).decode('utf-8')
    except AttributeError:
        return None


def send_to_worker(task, ip, port):
    client = make_client(dequeue_thrift.RPC, ip, port)
    client.task_service(task)


def send_to_taskqueue(task, task_id, ip, port):
    client = make_client(enqueue_thrift.RPC, ip, port)
    client.task_service(task, task_id)


def fetch_task(task_id):
    try:
        task = tasks[task_id]
        return task
    except KeyError:
        logger.error("task not found")
        return Task(None)


class Producer:

    def __init__(self):
        self.r = rconn
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
        send_to_taskqueue(data, task.id, master_ip, master_port)


class Worker:

    def __init__(self, ip, port):
        self.r = rconn
        self.id = md5((ip + str(port)).encode()).hexdigest()[:8]
        self.ip = ip
        self.port = port
        self.set_available()

    def set_available(self):
        self.r.set('worker:' + self.id + '.available', '1')

    def set_not_available(self, task_id):
        self.r.set('worker:' + self.id + '.available', '0')
        self.r.set('worker:' + self.id + '.current', task_id)

    def is_available(self):
        state = self.r.get('worker:' + self.id + '.available').decode('utf-8')
        if state == '0':
            return False
        else:
            return True

    def task_service(self, task):
        task = dill.loads(task)
        # add_task(task)
        self.set_not_available(task.id)
        self.work(task)

    def work(self, task):
        self.r.set(task.id, 'running')
        self.r.set('worker:' + self.id + '.current', task.id)
        task.running_time = time()
        try:
            run = types.FunctionType(task.data, globals(), 'run')
            task.result = run()
            self.r.set(task.id, 'finished')
            self.r.incr('worker:' + self.id + ".count_success")
        except Exception as error_msg:
            logger.error(error_msg)
            self.r.set(task.id, 'failed')
            self.r.incr('worker:' + self.id + ".count_failed")
            self.r.lpush('fail', task.id)
        task.running_time = time() - task.running_time
        self.set_available()
        return task.result


def add_worker(ip, port):
    worker = Worker(ip, port)
    workers.append(worker)
    rconn.lpush("workers", "{} {} {}".format(worker.id, ip, port))


def add_task(task, task_id):
    tasks[task_id] = task


def round_robin():
    offset = 0
    while True:
        if workers[offset].is_available():
            worker = workers[offset]
            task = tq.get()
            rconn.incr("output")
            send_to_worker(task['data'], worker.ip, worker.port)
            tasks[task['id']] = task['data']
        offset += 1
        offset = offset % len(workers)


class QueueHandler:

    def task_service(self, task, task_id):
        rconn.incr("input")
        tq.put({'data': task, 'id': task_id})
        tasks[task_id] = task


def listen():
    server = make_server(enqueue_thrift.RPC,
                         QueueHandler(), master_ip, master_port)
    server.serve()


def main():
    add_worker('127.0.0.1', 9089)
    add_worker('127.0.0.1', 9090)
    round_robin()


# Threading
if __name__ == '__main__':
    main_thread = threading.Thread(target=main)
    threads.append(main_thread)
    main_thread.start()

    listener_thread = threading.Thread(target=listen)
    threads.append(listener_thread)
    listener_thread.start()
