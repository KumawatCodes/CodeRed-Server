from fastapi import WebSocket, WebSocketDisconnect, status
from app.core.security import verify_token
from app.services.auth_service import AuthService
from app.database import get_db
from app.core.ws_manager import manager
from app.services.webSocket.matchmaking.matchmaking_service import matchmaking_service
from app.services.webSocket.matchmaking.match_service import match_service
import time

async def websocket_endpoint(websocket: WebSocket):
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    payload = verify_token(token)
    print("payload",payload)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async for db in get_db():
        user = await AuthService.get_user_by_id(db, int(user_id))
        break

    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    await manager.connect(user.user_id, websocket)

    await websocket.send_json({
        "type": "authenticated",
        "payload": {
            "user_id": user.user_id
        }
    })

    try:
        while True:

            data = await websocket.receive_json()

            if not isinstance(data, dict):
                continue

            event_type = data.get("type")
            payload = data.get("payload", {})

            if not event_type:
                continue

            if event_type == "join_queue":
                await matchmaking_service.join_queue(user.user_id)

            elif event_type == "code_update":
                await match_service.handle_progress(user.user_id, payload)

            elif event_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "payload": {
                        "timestamp": int(time.time())
                    }
                })

    except WebSocketDisconnect:
        await manager.disconnect(user.user_id)
        print(f"User {user.user_id} disconnected")

    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(user.user_id)