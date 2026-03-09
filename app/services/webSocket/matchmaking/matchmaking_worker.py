import asyncio
from app.core.redis import redis_client
from app.services.webSocket.matchmaking.match_service import match_service

MATCH_QUEUE = "matchmaking:queue"
MATCH_QUEUE_SET = "matchmaking:queue:set"

async def matchmaking_loop():
    while True:
        try:
            queue_length = await redis_client.llen(MATCH_QUEUE)

            if queue_length < 2:
                await asyncio.sleep(1)
                continue

            players = await redis_client.rpop(MATCH_QUEUE, 2)

            player1 = int(players[0])
            player2 = int(players[1])

            await match_service.create_match(player1, player2)

        except Exception as e:
            print("Matchmaking error:", e)
            await asyncio.sleep(1)