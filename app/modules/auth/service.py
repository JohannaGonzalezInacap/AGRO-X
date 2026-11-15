import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_token,
    new_opaque_token,
    verify_password,
)
from app.core.time import as_aware_utc
from app.modules.auth.models import AuditLog, RefreshToken, User
from app.modules.auth.schemas import LoginRequest, RegisterRequest

_bearer = HTTPBearer(auto_error=False)


def _audit(db: Session, request: Request, user_id: uuid.UUID | None, action: str) -> None:
    request_id = getattr(request.state, "request_id", "unknown")
    db.add(AuditLog(user_id=user_id, action=action, request_id=request_id))


def register_user(db: Session, request: Request, data: RegisterRequest) -> User:
    user = User(
        email=data.email.lower(),
        name=data.name,
        password_hash=hash_password(data.password),
        role=data.role.value,
        plan="free",
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise AppError(409, "email_taken", "Ya existe una cuenta con ese correo.") from exc
    _audit(db, request, user.id, "register")
    db.commit()
    return user


def _invalid_credentials() -> AppError:
    # Mismo mensaje y código si el correo no existe o la contraseña es incorrecta (ADR-002).
    return AppError(401, "invalid_credentials", "Correo o contraseña incorrectos.")


def _issue_tokens(db: Session, user: User, family_id: uuid.UUID) -> tuple[str, str]:
    settings = get_settings()
    access_token = create_access_token(user.id)
    refresh_token = new_opaque_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            family_id=family_id,
            token_hash=hash_token(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
        )
    )
    return access_token, refresh_token


def authenticate_user(db: Session, request: Request, data: LoginRequest) -> tuple[str, str]:
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        _audit(db, request, user.id if user else None, "login_failed")
        db.commit()
        raise _invalid_credentials()

    access_token, refresh_token = _issue_tokens(db, user, family_id=uuid.uuid4())
    _audit(db, request, user.id, "login_success")
    db.commit()
    return access_token, refresh_token


def rotate_refresh_token(db: Session, request: Request, refresh_token: str) -> tuple[str, str]:
    token_hash = hash_token(refresh_token)
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    if stored is None or stored.revoked or as_aware_utc(stored.expires_at) < datetime.now(UTC):
        raise AppError(401, "invalid_refresh_token", "El token de renovación no es válido.")

    if stored.used:
        # Reutilizar un token ya usado: se asume robo y se revoca toda la cadena (ADR-002).
        db.query(RefreshToken).filter(RefreshToken.family_id == stored.family_id).update(
            {"revoked": True}
        )
        _audit(db, request, stored.user_id, "refresh_reuse_detected")
        db.commit()
        raise AppError(401, "invalid_refresh_token", "El token de renovación no es válido.")

    stored.used = True
    user = db.get(User, stored.user_id)
    access_token, new_refresh_token = _issue_tokens(db, user, family_id=stored.family_id)
    _audit(db, request, user.id, "refresh")
    db.commit()
    return access_token, new_refresh_token


def revoke_refresh_token(db: Session, request: Request, refresh_token: str) -> None:
    token_hash = hash_token(refresh_token)
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if stored is not None:
        db.query(RefreshToken).filter(RefreshToken.family_id == stored.family_id).update(
            {"revoked": True}
        )
        _audit(db, request, stored.user_id, "logout")
        db.commit()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(401, "unauthorized", "Falta el token de acceso.")
    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise AppError(401, "unauthorized", "El token de acceso no es válido.") from exc

    user = db.get(User, user_id)
    if user is None:
        raise AppError(401, "unauthorized", "El token de acceso no es válido.")
    return user


def require_role(role: str):
    """Fábrica de dependencia: 403 forbidden si el rol de la cuenta no es el esperado."""

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != role:
            raise AppError(403, "forbidden", "Tu rol no tiene acceso a esta función.")
        return current_user

    return _dependency
