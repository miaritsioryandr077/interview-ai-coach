from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter()


@router.get("", summary="Health Check")
@router.get("/", summary="Health Check", include_in_schema=False)
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint verifying API service availability
    and database connectivity.
    """
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "version": "0.1.0"
    }

