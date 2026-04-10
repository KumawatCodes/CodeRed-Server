import redis.asyncio as redis
from app.config import settings

redis_client = redis.from_url(
    settings.UPSTASH_REDIS_URL,
    decode_responses=True
)