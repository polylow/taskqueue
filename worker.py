import thriftpy
from taskqueue import Worker, get_ip
from thriftpy.rpc import make_server
from hashlib import md5
import requests


dequeue_thrift = thriftpy.load("dequeue.thrift", module_name="dequeue_thrift")


ip = "127.0.0.1"
port = 9090


def listen(port=9090):
    server = make_server(dequeue_thrift.RPC, Worker(ip, port), ip, port)
    server.serve()

if __name__ == '__main__':
    print("ID:", md5((ip + str(port)).encode()).hexdigest()[:8])
    listen(port)
