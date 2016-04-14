import thriftpy
from taskqueue import Worker
from thriftpy.rpc import make_server


rpc_thrift = thriftpy.load("rpc.thrift", module_name="rpc_thrift")


def listen(port=9090):
    server = make_server(rpc_thrift.RPC, Worker("172.16.1.137", 9090), '172.16.1.137', port)
    server.serve()

if __name__ == '__main__':
    listen(9090)
