import thriftpy
from taskqueue import Worker
from thriftpy.rpc import make_server
from hashlib import md5


dequeue_thrift = thriftpy.load("dequeue.thrift", module_name="dequeue_thrift")


ip = "172.16.0.170"
port = 9090

def listen(port=9090):
    server = make_server(dequeue_thrift.RPC, Worker(ip , port), ip, port)
    server.serve()

if __name__ == '__main__':
    print(md5((ip+str(port)).encode()).hexdigest()[:8])
    listen(port)
