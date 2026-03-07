import uuid
from app.core.redis import redis_client
from app.core.ws_manager import manager
from app.services.webSocket.matchmaking.match_listener import match_listener

MATCH_QUEUE_SET = "matchmaking:queue:set"

class MatchService:

    async def create_match(self, player1: int, player2: int):

        match_id = str(uuid.uuid4())

        await redis_client.hset(
            f"match:{match_id}",
            mapping={
                "player1": player1,
                "player2": player2,
                "status": "active"
            }
        )
        await redis_client.srem(MATCH_QUEUE_SET, player1)
        await redis_client.srem(MATCH_QUEUE_SET, player2)

        await redis_client.set(f"user:match:{player1}", match_id)
        await redis_client.set(f"user:match:{player2}", match_id)

        await manager.send_to_user(player1, {
            "type": "match_found",
            "payload": {"match_id": match_id}
        })

        await manager.send_to_user(player2, {
            "type": "match_found",
            "payload": {"match_id": match_id}
        })

        await redis_client.publish(f"match:{match_id}",
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


match_service = MatchService()