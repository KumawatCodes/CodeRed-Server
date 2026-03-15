import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    """Application factory pattern for better testability"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add middleware
    setup_middleware(app)

    # Add routes
    setup_routes(app)

    # Add event handlers
    setup_events(app)

    return app

def setup_middleware(app: FastAPI) -> None:
    """setup all middleware"""

    # Allow both your frontend URLs
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
    """Setup all API routes"""

    # REST API
    # from app.api.v1.endpoints import auth
    from app.api.v1.endpoints import submission
    from app.api.v1.endpoints import problem
    from app.api.v1.endpoints import users
    from app.api.v1.endpoints import friends
    from app.api.v1.endpoints import auth
    from app.api.v2.endpoints import user
    # from app.api.v2.endpoints import auth
    from app.api.v2.endpoints import code_execution
    #authentication APIs
    app.include_router(
        auth.router,
        prefix="/api/v1",
        tags=["Auth"]
    )
    # code Submission APIs
    app.include_router(
        submission.router,
        prefix="/api/v1/submission",
        tags=["Submissions"]
    )
    # problem APIs
    app.include_router(
        problem.router,
        prefix="/api/v1",
        tags=["Problems"]
    )
    # User APIs
    app.include_router(
        users.router,
        prefix="/api/v1",
        tags=["users"]
    )
    # Friends ID
    app.include_router(
        friends.router,
        prefix="/api/v1/friends",
        tags=["friends"]
    )

    #Websocket route
    app.add_api_websocket_route("/ws",websocket_endpoint)

    # app.include_router(
    #     user.router,
    #     prefix="/api/v2/user",
    #     tags=["user"]
    # )
    # app.include_router(
    #     auth.router,
    #     prefix="/api/v2/auth",
    #     tags=["auth"]
    # )
    # app.include_router(
    #     code_execution.router,
    #     prefix="/api/v2/execution",
    #     tags=["code execution"]
    # )
    #Websocket route
    # app.add_api_websocket_route("/ws",websocket_endpoint)


def setup_events(app: FastAPI) -> None:
    """Setup startup/shutdown events"""

    @app.on_event("startup")
    async def startup_event():

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(" Database tables created successfully")

        # background workers
        await manager.start_listener()
        asyncio.create_task(event_listener())

    @app.get("/")
    async def root():
        return {
            "message": "CodeForge API is running!",
            "version": settings.VERSION,
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "CodeForge API"}

def setup_events(app: FastAPI) -> None:
    """Setup startup/shutdown events"""

    @app.on_event("startup")
    async def startup_event():

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(" Database tables created successfully")
        await manager.start_listener()

        asyncio.create_task(matchmaking_loop())

app = create_application()