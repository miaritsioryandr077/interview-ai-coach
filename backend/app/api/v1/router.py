from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, users, documents, contexts, progress, sessions

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(contexts.router, prefix="/contexts", tags=["Contexts"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Interview Sessions"])
api_router.include_router(progress.router, tags=["Progress"])
