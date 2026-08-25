from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.api.v1.router import api_router
from app.db.base import Base  # noqa: F401 — enregistre tous les modèles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create missing tables on startup (idempotent — never drops existing data)."""
    Base.metadata.create_all(bind=engine, checkfirst=True)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    """
    Root endpoint returning API metadata.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"], summary="Top-level Health Check")
def health_check() -> dict[str, str]:
    """
    Simple health check endpoint returning API status.
    """
    return {"status": "healthy"}
