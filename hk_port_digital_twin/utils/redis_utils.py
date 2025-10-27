import redis
import os

def get_redis_connection(host="localhost", port=6379):
    """Establishes a connection to Redis."""
    return redis.Redis(host=host, port=port, db=0)