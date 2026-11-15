from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.privacy import service
from app.modules.privacy.schemas import (
    ConsentsResponse,
    ConsentsUpdate,
    DataExportResponse,
)

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.get("/export", response_model=DataExportResponse)
def export_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DataExportResponse:
    return service.get_data_export(db, current_user, request)


@router.get("/consents", response_model=ConsentsResponse)
def get_consents(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ConsentsResponse:
    return service.get_consents(db, current_user)


@router.put("/consents", response_model=ConsentsResponse)
def update_consents(
    request: Request,
    data: ConsentsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConsentsResponse:
    return service.update_consents(db, current_user, request, data)


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service.delete_account(db, current_user, request)
