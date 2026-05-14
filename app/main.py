import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.models.user import User
from app.models.submission import Submission
from app.core.websocket import websocket_endpoint
from app.core.ws_manager import manager
from app.core.event_listener import event_listener
import logging

logging.basicConfig(level=logging.INFO)

from app.config import settings
from app.database import engine, Base

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    setup_middleware(app)
    setup_routes(app)
    setup_events(app)

    # Prometheus: exposes /metrics endpoint
    Instrumentator().instrument(app).expose(app)

    return app

def setup_middleware(app: FastAPI) -> None:
    origins = [
        "http://10.166.76.250:3000",
        "http://localhost:3000",
        "https://alphonse-semimature-idiocratically.ngrok-free.dev",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def setup_routes(app: FastAPI) -> None:
    from app.api.v1.endpoints import submission, problem, users, friends, auth
    from app.api.v2.endpoints import user, auths, code_execution

    app.include_router(auth.router,           prefix="/api/v1",          tags=["Auth"])
    app.include_router(submission.router,     prefix="/api/v1/submission",tags=["Submissions"])
    app.include_router(problem.router,        prefix="/api/v1",          tags=["Problems"])
    app.include_router(users.router,          prefix="/api/v1",          tags=["users"])
    app.include_router(friends.router,        prefix="/api/v1/friends",  tags=["friends"])
    app.include_router(user.router,           prefix="/api/v2/user",     tags=["user"])
    app.include_router(auths.router,          prefix="/api/v2/auth",     tags=["auth"])
    app.include_router(code_execution.router, prefix="/api/v2/execution",tags=["code execution"])
    app.add_api_websocket_route("/ws", websocket_endpoint)

def setup_events(app: FastAPI) -> None:

    @app.on_event("startup")
    async def startup_event():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully")
        await manager.start_listener()
        app.state.listener_task = asyncio.create_task(event_listener())

    @app.on_event("shutdown")
    async def shutdown():
        task = app.state.listener_task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @app.get("/")
    async def root():
        return {"message": "CodeRed API is running!", "version": settings.VERSION, "docs": "/docs"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "CodeRed API"}

app = create_application()