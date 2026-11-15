from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rate_limit import enforce_login_rate_limit
from app.modules.auth import service
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)) -> User:
    enforce_login_rate_limit(request, "register")
    return service.register_user(db, request, data)


@router.post("/login", response_model=TokenResponse)
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    enforce_login_rate_limit(request, "login")
    access_token, refresh_token = service.authenticate_user(db, request, data)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, data: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access_token, refresh_token = service.rotate_refresh_token(db, request, data.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, data: LogoutRequest, db: Session = Depends(get_db)) -> None:
    service.revoke_refresh_token(db, request, data.refresh_token)


@router.get("/me", response_model=UserProfileResponse)
def me(current_user: User = Depends(service.get_current_user)) -> User:
    return current_user
