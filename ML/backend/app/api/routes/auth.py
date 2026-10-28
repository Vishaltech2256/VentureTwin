from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.services import auth_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.security import create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dict)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    auth_service.register_user(db, user_data)
    return {"message": "User registered successfully"}

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    credentials = UserLogin(
        email=form_data.username,
        password=form_data.password
    )

    user = auth_service.authenticate_user(db, credentials)

    access_token = create_access_token(subject=user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get information about the currently logged-in user.
    """
    return current_user
