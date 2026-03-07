from app.core.redis import redis_client

MATCH_QUEUE = "matchmaking:queue"
MATCH_QUEUE_SET = "matchmaking:queue:set"

class MatchmakingService:


    async def join_queue(self, user_id: int):

        exists = await redis_client.sismember(MATCH_QUEUE_SET, user_id)

        if exists:
            return

        await redis_client.sadd(MATCH_QUEUE_SET, user_id)
        await redis_client.lpush(MATCH_QUEUE, user_id)

matchmaking_service = MatchmakingService()