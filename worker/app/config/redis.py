import os
import redis

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError("REDIS_URL is not set")

def get_redis_client():
    return redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True
    )
