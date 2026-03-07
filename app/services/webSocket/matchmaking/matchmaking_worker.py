import asyncio
from app.core.redis import redis_client
from app.services.webSocket.matchmaking.match_service import match_service

MATCH_QUEUE = "matchmaking:queue"

async def matchmaking_loop():

    while True:

        players = await redis_client.rpop(MATCH_QUEUE, 2)

        if not players or len(players) < 2:
            await asyncio.sleep(1)
            continue

        player1 = int(players[0])
        player2 = int(players[1])

        await match_service.create_match(player1, player2)