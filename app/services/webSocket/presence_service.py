import json
from app.core.redis import redis_client

Presence_Channel = "presence"
class PresenceService:

  @staticmethod
  async def publish_user_online(user_id:int):
    redis_client.publish(Presence_Channel,json.dumps({
      "type": "USER_ONLINE",
      "user_id": user_id
    }))
  @staticmethod
  async def publish_user_offline(user_id:int):
    redis_client.publish(Presence_Channel,json.dumps({
      "type": "USER_OFFLINE",
      "user_id": user_id
    }))