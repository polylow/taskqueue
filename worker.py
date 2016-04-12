import thriftpy
from taskqueue import Worker
from thriftpy.rpc import make_server

rpc_thrift = thriftpy.load("rpc.thrift", module_name="rpc_thrift")

def listen(port=9090):
    server = make_server(rpc_thrift.RPC, Worker(), '127.0.0.1', port)
    server.serve()

if __name__ == '__main__':
    worker = Worker()
    listen(9090)
