import thriftpy
from taskqueue import Worker
from thriftpy.rpc import make_server
from hashlib import md5


rpc_thrift = thriftpy.load("rpc.thrift", module_name="rpc_thrift")


ip = "172.16.1.137"
port = 9090

def listen(port=9090):
    server = make_server(rpc_thrift.RPC, Worker(ip , port), ip, port)
    server.serve()

if __name__ == '__main__':
    print(md5((ip+str(port)).encode()).hexdigest()[:8])
    listen(port)
