import redis
from taskqueue import redis_ip, redis_port


rconn = redis.Redis(redis_ip, redis_port)

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
