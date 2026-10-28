from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    RefreshTokenRequest,
    UserUpdate,
)
from app.services import auth_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_password_hash,
)

router = APIRouter(tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user. Returns the created user profile.
    """
    user = auth_service.register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Log in with JSON (email & password) or OAuth2 form-data (username & password).
    Returns both access_token and refresh_token.
    """
    content_type = request.headers.get("content-type", "")
    email: Optional[str] = None
    password: Optional[str] = None

    if "application/json" in content_type:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
    else:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required.",
        )

    credentials = UserLogin(email=email, password=password)
    user = auth_service.authenticate_user(db, credentials)

    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/token", response_model=Token)
async def login_oauth2_token(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    OAuth2 token endpoint alias for form-encoded login requests.
    """
    return await login(request=request, db=db)


@router.post("/refresh", response_model=Token)
def refresh_token_endpoint(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a new access token and refresh token using a valid refresh token.
    """
    payload = decode_refresh_token(data.refresh_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload["sub"]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    new_access_token = create_access_token(subject=user.email)
    new_refresh_token = create_refresh_token(subject=user.email)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get information about the currently logged-in user.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update profile details for the authenticated user.
    """
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    if update_data.email is not None and update_data.email != current_user.email:
        # Check duplicate
        exists = db.query(User).filter(User.email == update_data.email).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        current_user.email = update_data.email
    if update_data.password is not None:
        current_user.password_hash = get_password_hash(update_data.password)

    db.commit()
    db.refresh(current_user)
    return current_user
