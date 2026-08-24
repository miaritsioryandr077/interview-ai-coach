from typing import Any, Union
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from app.services.auth import auth_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register new user")
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Register a new user account with email, password, and full name.
    """
    return auth_service.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=Token, summary="User Login (Returns JWT Access Token)")
async def login(
    request: Request,
    db: Session = Depends(get_db),
) -> Any:
    """
    Authenticate user and issue JWT access token.
    Supports both JSON body (`{"email": "...", "password": "..."}`) and OAuth2 Form Data (`username=...&password=...`).
    """
    email = None
    password = None

    content_type = request.headers.get("content-type", "")

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        try:
            body = await request.json()
            email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/Username and Password are required.",
        )

    user = auth_service.authenticate_user(db=db, email=email, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    access_token = auth_service.create_user_token(user=user)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse, summary="Get Current Authenticated User Profile")
def get_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Fetch the currently authenticated user details.
    """
    return current_user
