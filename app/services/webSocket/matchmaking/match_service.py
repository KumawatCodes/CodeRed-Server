import uuid
import json
from app.core.redis import redis_client
from app.core.ws_manager import manager
from app.services.webSocket.matchmaking.match_listener import match_listener
from app.services.user_service import UserService

MATCH_QUEUE_SET = "matchmaking:queue:set"

class MatchService:

    async def create_match(self, player1: int, player2: int):

        match_id = str(uuid.uuid4())

        await redis_client.hset(
            f"match:{match_id}",
            mapping={
                "player1": player1,
                "player2": player2,
                "player1_submitted": 0,
                "player2_submitted": 0,
                "status": "active"
            }
        )
        await redis_client.expire(f"match:{match_id}", 3600)

        await redis_client.srem(MATCH_QUEUE_SET,player1)
        await redis_client.srem(MATCH_QUEUE_SET,player2)

        await redis_client.set(f"user:match:{player1}", match_id, ex=3600)
        await redis_client.set(f"user:match:{player2}", match_id, ex=3600)

        await redis_client.publish(
            "match_events",
            json.dumps({
                "type": "match_found",
                "match_id": match_id,
                "player1": player1,
                "player2": player2
            })
        )
    async def handle_progress(self, user_id: int, payload: dict):

        match_id = await redis_client.get(f"user:match:{user_id}")

        if not match_id:
            return

        match_id = match_id.decode()

        match = await redis_client.hgetall(f"match:{match_id}")

        player1 = int(match["player1"])
        player2 = int(match["player2"])

        opponent = player2 if user_id == player1 else player1

        await redis_client.publish(
            "match_events",
            json.dumps({
                "type": "progress",
                "match_id": match_id,
                "user_id": user_id,
                "progress": payload.get("progress")
            })
        )

    async def resume_match(self, user_id: int):

        match_id = await redis_client.get(f"user:match:{user_id}")
        match = await redis_client.hgetall(f"match:{match_id}")

        if not match or not match_id:
            await redis_client.publish(
            "match_events",
            json.dumps({
                "type" : "resume_match_not_found",
                "user": user_id
            }))
            return

        player1 = int(match["player1"])
        player2 = int(match["player2"])

        await redis_client.publish(
            "match_events",
            json.dumps({
                "type" : "resume_match",
                "match_id": match_id,
                "player1": player1,
                "player2": player2
            }))

    async def end_match(self, match_id: str):
        print("this endmathc match service also called")
        match = await redis_client.hgetall(f"match:{match_id}")

        player1 = int(match["player1"])
        player2 = int(match["player2"])

        # notify both players
        await redis_client.publish(
            "match_events",
            json.dumps({
                "type": "match_end",
                "match_id": match_id,
                "players": [player1, player2]
            })
        )
        # cleanup Redis
        await redis_client.delete(f"match:{match_id}")
        await redis_client.delete(f"user:match:{player1}")
        await redis_client.delete(f"user:match:{player2}")

    async def submit_code(self, user_id: int):

        match_id = await redis_client.get(f"user:match:{user_id}")
        if not match_id:
            return

        match_id = match_id.decode()

        match = await redis_client.hgetall(f"match:{match_id}")

        player1 = int(match["player1"])
        player2 = int(match["player2"])

        # determine which player submitted
        if user_id == player1:
            await redis_client.hset(f"match:{match_id}", "player1_submitted", 1)
        else:
            await redis_client.hset(f"match:{match_id}", "player2_submitted", 1)

        await redis_client.delete(f"user:match:{user_id}")

        # check if both submitted
        match = await redis_client.hgetall(f"match:{match_id}")

        p1_done = int(match[b"player1_submitted"])
        p2_done = int(match[b"player2_submitted"])

        if p1_done and p2_done:
            await self.end_match(match_id)

        opponent = player1 if user_id == player2 else player2
        # notify opponent that someone finished
        await redis_client.publish(
            "match_events",
            json.dumps({
                "type": "user_submitted",
                "match_id": match_id,
                "user_id": user_id,
                "opponent": opponent
            })
        )

match_service = MatchService()