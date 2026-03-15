from app.core.redis import redis_client

MATCH_QUEUE = "matchmaking:queue"
MATCH_QUEUE_SET = "matchmaking:queue:set"

class MatchmakingService:


    async def join_queue(self, user_id: int):

        added = await redis_client.sadd(MATCH_QUEUE_SET, user_id)

        if not added :
            return

        await redis_client.lpush(MATCH_QUEUE, user_id)
    async def leave_queue(self, user_id: int):

        await redis_client.srem(MATCH_QUEUE_SET, user_id)
        await redis_client.lrem(MATCH_QUEUE,0, user_id)

matchmaking_service = MatchmakingService()