from typing import List
from app.core.redis import redis_client

ONLINE_USERS_KEY = "online_users"

async def add_online_user(user_id: int):
    await redis_client.sadd(ONLINE_USERS_KEY, user_id)

async def remove_online_user(user_id: int):
    await redis_client.srem(ONLINE_USERS_KEY, user_id)

async def get_online_users() -> List[int]:
    users = await redis_client.smembers(ONLINE_USERS_KEY)
    return [int(u) for u in users]

async def get_online_friends(user_id: int, friend_ids: List[int]) -> List[int]:
    online_users = await redis_client.smembers(ONLINE_USERS_KEY)
    online_users = set(map(int, online_users))
    return list(online_users.intersection(set(friend_ids)))