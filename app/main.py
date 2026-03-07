import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.user import User
from app.models.submission import Submission
from app.core.websocket import websocket_endpoint
from app.core.ws_manager import manager
from app.services.webSocket.matchmaking.matchmaking_worker import matchmaking_loop


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
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://ec3d0556de7f.ngrok-free.app",
        "http://localhost:8000",

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
    from app.api.v2.endpoints import user
    from app.api.v2.endpoints import auth
    # authentication APIs
    # app.include_router(
    #     auth.router,
    #     prefix="/api/v1",
    #     tags=["Auth"]
    # )
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
<<<<<<< HEAD
    app.include_router(
        user.router,
        prefix="/api/v2/user",
        tags=["user"]
    )
    app.include_router(
        auth.router,
        prefix="/api/v2/auth",
        tags=["auth"]
    )
def setup_events(app: FastAPI) -> None:
    """Setup startup/shutdown events"""

    @app.on_event("startup")
    async def startup_event():

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(" Database tables created successfully")
=======
    #Added websocket route
    app.add_api_websocket_route("/ws",websocket_endpoint)
>>>>>>> 5b52b944073665000322ecf8cb4c549095f25ce1

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
