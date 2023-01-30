import redis
from config import REDIS_DB, REDIS_HOST, REDIS_PORT

pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
)

redis_client = redis.Redis(connection_pool=pool)
