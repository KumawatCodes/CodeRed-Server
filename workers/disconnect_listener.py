import asyncio
from app.core.redis import redis_client
from app.services.webSocket.matchmaking.match_service import match_service


class DisconnectListener:

    async def start(self):

        pubsub = redis_client.pubsub()

        await pubsub.psubscribe("__keyevent@0__:expired")

        async for message in pubsub.listen():

            if message["type"] != "pmessage":
                continue

            key = message["data"]

            if key.startswith("disconnect:"):

                user_id = int(key.split(":")[1])

                match_id = await redis_client.get(f"user:match:{user_id}")

                if not match_id:
                    continue

                await match_service.end_match(match_id)

if __name__ == "__main__":
    listener = DisconnectListener()
    asyncio.run(listener.start())