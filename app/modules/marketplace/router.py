import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user, require_role
from app.modules.marketplace import service
from app.modules.marketplace.models import MerchantProfile
from app.modules.marketplace.schemas import (
    MerchantProfileResponse,
    MerchantProfileUpsert,
    SurplusCreate,
    SurplusResponse,
    SurplusStatusUpdate,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

_require_merchant = require_role("merchant")
_require_producer = require_role("producer")


@router.put("/merchant-profile", response_model=MerchantProfileResponse)
def upsert_merchant_profile(
    data: MerchantProfileUpsert,
    merchant: User = Depends(_require_merchant),
    db: Session = Depends(get_db),
) -> MerchantProfile:
    return service.upsert_merchant_profile(db, merchant, data)


@router.get("/merchants", response_model=list[MerchantProfileResponse])
def list_merchants(
    producer: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> list[MerchantProfile]:
    return service.list_merchants(db, producer)


@router.post("/surplus", response_model=SurplusResponse, status_code=status.HTTP_201_CREATED)
def create_surplus(
    data: SurplusCreate, producer: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> SurplusResponse:
    surplus = service.create_surplus(db, producer, data)
    return service.to_response(surplus, producer)


@router.get("/surplus", response_model=list[SurplusResponse])
def list_surplus(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[SurplusResponse]:
    items = service.list_surplus(db, user)
    return [service.to_response(s, user) for s in items]


@router.patch("/surplus/{surplus_id}", response_model=SurplusResponse)
def update_surplus_status(
    surplus_id: uuid.UUID,
    data: SurplusStatusUpdate,
    producer: User = Depends(_require_producer),
    db: Session = Depends(get_db),
) -> SurplusResponse:
    surplus = service.update_surplus_status(db, producer, surplus_id, data)
    return service.to_response(surplus, producer)
