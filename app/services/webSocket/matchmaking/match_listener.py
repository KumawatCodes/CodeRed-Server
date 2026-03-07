import asyncio
import json
from app.core.redis import redis_client
from app.core.ws_manager import manager

class MatchListener:

    def __init__(self):
        self.pubsub = redis_client.pubsub()

    async def subscribe(self, match_id: str):
        await self.pubsub.subscribe(f"match:{match_id}")

    async def listen(self):

        async for message in self.pubsub.listen():

            if message["type"] != "message":
                continue

            data = json.loads(message["data"])

            event_type = data["type"]
            payload = data["payload"]

            if event_type == "opponent_progress":

                opponent_id = payload["opponent_id"]

                await manager.send_to_user(opponent_id, {
                    "type": "opponent_progress",
                    "payload": payload
                })


match_listener = MatchListener()