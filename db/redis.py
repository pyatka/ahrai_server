from flask import g
import redis

from settings import DB

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = redis.Redis(**DB["redis"])

    return g.redis