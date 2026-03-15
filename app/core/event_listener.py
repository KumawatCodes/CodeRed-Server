import json
from app.core.redis import redis_client
from app.core.ws_manager import manager
from app.services.user_service import UserService
from app.database import AsyncSessionLocal


async def event_listener():

    pubsub = redis_client.pubsub()
    await pubsub.subscribe("match_events")

    async for msg in pubsub.listen():

        if msg["type"] != "message":
            continue

        event = json.loads(msg["data"])

        if event["type"] == "match_found":

            player1 = event["player1"]
            player2 = event["player2"]
            print("match_found:: ",player1,player2)
            match_id = event["match_id"]

            async with AsyncSessionLocal() as db:
                p1 = await UserService.get_user_by_user_id(db, player1)
                p2 = await UserService.get_user_by_user_id(db, player2)

            await manager.send_to_user(player1, {
                "type": "match_found",
                "payload": {
                    "match_id": match_id,
                    "matchSource":"found",
                    "opponent": {
                        "id": p2.user_id,
                        "username": p2.username,
                        "avatar": p2.profile_picture,
                        "rank": p2.current_rank
                    }
                }
            })

            await manager.send_to_user(player2, {
                "type": "match_found",
                "payload": {
                    "match_id": match_id,
                    "matchSource":"found",
                    "opponent": {
                        "id": p1.user_id,
                        "username": p1.username,
                        "avatar": p1.profile_picture,
                        "rank": p1.current_rank
                    }
                }
            })

        if event["type"] == "resume_match_not_found":
            user = event["user"]
            await manager.send_to_user(user, {
                "type": "resume_match_not_found"
            })

        if event["type"] == "match_end":
            for player in event["players"]:
                await manager.send_to_user(player, {
                    "type": "match_end",
                })




        if event["type"] == "resume_match":
            # opponent_id = player2 if user_id == player1 else player1
            user1 = event["player1"]
            user2 = event["player2"]
            async with AsyncSessionLocal() as db:
                player1 = await UserService.get_user_by_user_id(db, user1)
                player2 = await UserService.get_user_by_user_id(db, user2)

            player1_info = {
                "id": player1.user_id,
                "username": player1.username,
                "avatar": player1.profile_picture,
                "rank": player1.current_rank
            }

            player2_info = {
                "id": player2.user_id,
                "username": player2.username,
                "avatar": player2.profile_picture,
                "rank": player2.current_rank
            }

            await manager.send_to_user(user1, {
                "type": "resume_match",
                "payload": {
                    "match_id": match_id,
                    "matchSource":"resume",
                    "opponent": player2_info
                }
            })

            await manager.send_to_user(user2, {
                "type": "resume_match",
                "payload": {
                    "match_id": match_id,
                    "matchSource":"resume",
                    "opponent": player1_info
                }
            })

        if event["type"] == "user_submitted":
            user = event["user_id"]
            opponent = event["opponent"]
            match_id = event["match_id"]

            await manager.send_to_user(opponent,{
                "type": "opponent_submitted",
                "payload": {
                    "match_id": match_id,
                    "opponent": user
                }
            })

            await manager.send_to_user(user,{
                "type": "submit_successful",
                "payload": {
                    "match_id": match_id,
                    "opponent": opponent
                }
            })
