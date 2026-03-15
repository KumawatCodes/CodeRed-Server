import asyncio
from app.core.redis import redis_client
from app.services.webSocket.matchmaking.match_service import match_service

MATCH_QUEUE = "matchmaking:queue"


async def matchmaking_loop():

    while True:
        try:

            # wait for first player
            _, player1 = await redis_client.brpop(MATCH_QUEUE)

            # wait for second player
            while True:
                _, player2 = await redis_client.brpop(MATCH_QUEUE)
                if(player1 != player2):
                    break

            player1 = int(player1)
            player2 = int(player2)

            print("match created: ",player1,player2)
            await match_service.create_match(player1, player2)

        except Exception as e:
            print("Matchmaking error:", e)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(matchmaking_loop())