import asyncio
from fastapi import WebSocket
from app.core.redis import redis_client
import json
import uuid

INSTANCE_ID = str(uuid.uuid4())

ONLINE_KEY = "online:user:{user_id}"
INSTANCE_CHANNEL = "ws:instance:{instance_id}"


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.pubsub = redis_client.pubsub()

    async def start_listener(self):
        asyncio.create_task(self._listen())

    async def _listen(self):

        await self.pubsub.subscribe(
            INSTANCE_CHANNEL.format(instance_id=INSTANCE_ID)
        )

        async for message in self.pubsub.listen():

            if message["type"] != "message":
                continue

            data = json.loads(message["data"])

            user_id = data["user_id"]
            payload = data["message"]

            websocket = self.active_connections.get(user_id)

            if websocket:
                try:
                    await websocket.send_json(payload)
                except:
                    await self.disconnect(user_id)

    async def connect(self, user_id: int, websocket: WebSocket):

        existing = self.active_connections.get(user_id)

        if existing:
            try:
                await existing.close()
            except:
                pass

        self.active_connections[user_id] = websocket

        # if user is in match already
        await redis_client.delete(f"disconnect:{user_id}")

        await redis_client.set(
            ONLINE_KEY.format(user_id=user_id),
            INSTANCE_ID,
            ex=60
        )

        asyncio.create_task(self.heartbeat(user_id))

    async def disconnect(self, user_id: int):

        if user_id in self.active_connections:
            self.active_connections.pop(user_id, None)

        # Ending Match in 60 sec
        await redis_client.set(f"disconnect:{user_id}",1,ex=60)

        await redis_client.delete(
            ONLINE_KEY.format(user_id=user_id)
        )

    async def heartbeat(self, user_id: int):

        while user_id in self.active_connections:

            await redis_client.expire(
                ONLINE_KEY.format(user_id=user_id),
                60
            )
            await asyncio.sleep(20)

    async def send_to_user(self, user_id: int, message: dict):

        websocket = self.active_connections.get(user_id)

        if websocket:
            try:
                await websocket.send_json(message)
                return
            except:
                await self.disconnect(user_id)
                return

        instance_id = await redis_client.get(
            ONLINE_KEY.format(user_id=user_id)
        )

        if not instance_id:
            return

        instance_id = instance_id.decode()

        await redis_client.publish(
            INSTANCE_CHANNEL.format(instance_id=instance_id),
            json.dumps({
                "user_id": user_id,
                "message": message
            })
        )


manager = ConnectionManager()