import uuid
import json
from app.core.redis import redis_client
from app.core.ws_manager import manager
from app.services.webSocket.matchmaking.match_listener import match_listener
from app.services.user_service import UserService
from app.database import AsyncSessionLocal

MATCH_QUEUE_SET = "matchmaking:queue:set"


class MatchService:

    async def create_match(self, player1: int, player2: int):

        match_id = str(uuid.uuid4())

        # Store match session
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

        # Remove players from matchmaking queue
        await redis_client.srem(MATCH_QUEUE_SET, player1)
        await redis_client.srem(MATCH_QUEUE_SET, player2)

        # Map user -> match
        await redis_client.set(f"user:match:{player1}", match_id, ex=3600)
        await redis_client.set(f"user:match:{player2}", match_id, ex=3600)

        # Fetch player info from database
        async with AsyncSessionLocal() as db:
            player1_data = await UserService.get_user_by_user_id(db, player1)
            player2_data = await UserService.get_user_by_user_id(db, player2)

        player1_info = {
            "id": player1_data.user_id,
            "username": player1_data.username,
            "avatar": player1_data.profile_picture,
            "rank": player1_data.current_rank
        }

        player2_info = {
            "id": player2_data.user_id,
            "username": player2_data.username,
            "avatar": player2_data.profile_picture,
            "rank": player2_data.current_rank
        }

        # Send match_found to player1
        await manager.send_to_user(player1, {
            "type": "match_found",
            "payload": {
                "match_id": match_id,
                "opponent": player2_info
            }
        })

        # Send match_found to player2
        await manager.send_to_user(player2, {
            "type": "match_found",
            "payload": {
                "match_id": match_id,
                "opponent": player1_info
            }
        })

        # Publish match start event
        await redis_client.publish(
            f"match:{match_id}",
            json.dumps({
                "type": "match_start",
                "payload": {
                    "player1": player1,
                    "player2": player2
                }
            })
        )

        await match_listener.subscribe(match_id)

    async def handle_progress(self, user_id: int, payload: dict):

        match_id = await redis_client.get(f"user:match:{user_id}")

        if not match_id:
            return

        match_id = match_id.decode()

        match = await redis_client.hgetall(f"match:{match_id}")

        player1 = int(match[b"player1"])
        player2 = int(match[b"player2"])

        opponent = player2 if user_id == player1 else player1

        await redis_client.publish(
            f"match:{match_id}",
            json.dumps({
                "type": "opponent_progress",
                "payload": {
                    "opponent_id": opponent,
                    "progress": payload.get("progress")
                }
            })
        )

    async def resume_match(self, user_id: int):

        match_id = await redis_client.get(f"user:match:{user_id}")

        if not match_id:
            return

        match_id = match_id.decode()

        match = await redis_client.hgetall(f"match:{match_id}")

        if not match:
            return

        player1 = int(match[b"player1"])
        player2 = int(match[b"player2"])

        opponent_id = player2 if user_id == player1 else player1

        async with AsyncSessionLocal() as db:
            opponent_data = await UserService.get_user_by_user_id(db, opponent_id)

        opponent_info = {
            "id": opponent_data.user_id,
            "username": opponent_data.username,
            "avatar": opponent_data.profile_picture,
            "rank": opponent_data.current_rank
        }

        await manager.send_to_user(user_id, {
            "type": "match_resume",
            "payload": {
                "match_id": match_id,
                "opponent": opponent_info
            }
        })

    async def end_match(self, match_id: str):

        match = await redis_client.hgetall(f"match:{match_id}")

        player1 = int(match[b"player1"])
        player2 = int(match[b"player2"])

        # notify both players
        await manager.send_to_user(player1, {
            "type": "match_end"
        })

        await manager.send_to_user(player2, {
            "type": "match_end"
        })

        # cleanup Redis
        await redis_client.delete(f"match:{match_id}")

async def submit_code(self, user_id: int):

    match_id = await redis_client.get(f"user:match:{user_id}")
    if not match_id:
        return

    match_id = match_id.decode()

    match = await redis_client.hgetall(f"match:{match_id}")

    player1 = int(match[b"player1"])
    player2 = int(match[b"player2"])

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

    opponent = player1 if user_id == player1 else player2
    # notify opponent that someone finished
    await manager.send_to_user(opponent, {
        "type": "opponent_submitted",
        "payload": {"user_id": user_id}
    })
match_service = MatchService()