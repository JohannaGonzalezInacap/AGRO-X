import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth.models import User
from app.modules.auth.service import require_role
from app.modules.farms import service
from app.modules.farms.models import CropHistory, Farm
from app.modules.farms.schemas import (
    CropHistoryCreate,
    CropHistoryResponse,
    CropStageUpdate,
    FarmCreate,
    FarmResponse,
    FarmUpdate,
)

router = APIRouter(prefix="/farms", tags=["farms"])

_require_producer = require_role("producer")


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(
    data: FarmCreate, owner: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> Farm:
    return service.create_farm(db, owner, data)


@router.get("", response_model=list[FarmResponse])
def list_farms(
    owner: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> list[Farm]:
    return service.list_farms(db, owner)


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: uuid.UUID, owner: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> Farm:
    return service.get_owned_farm_or_404(db, owner, farm_id)


@router.patch("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: uuid.UUID,
    data: FarmUpdate,
    owner: User = Depends(_require_producer),
    db: Session = Depends(get_db),
) -> Farm:
    return service.update_farm(db, owner, farm_id, data)


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: uuid.UUID, owner: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> None:
    service.delete_farm(db, owner, farm_id)


@router.post(
    "/{farm_id}/crop-history",
    response_model=CropHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_crop(
    farm_id: uuid.UUID,
    data: CropHistoryCreate,
    owner: User = Depends(_require_producer),
    db: Session = Depends(get_db),
) -> CropHistory:
    return service.register_crop(db, owner, farm_id, data)


@router.get("/{farm_id}/crop-history", response_model=list[CropHistoryResponse])
def list_crop_history(
    farm_id: uuid.UUID, owner: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> list[CropHistory]:
    return service.list_crop_history(db, owner, farm_id)


@router.patch("/{farm_id}/crop-history/current", response_model=CropHistoryResponse)
def advance_current_stage(
    farm_id: uuid.UUID,
    data: CropStageUpdate,
    owner: User = Depends(_require_producer),
    db: Session = Depends(get_db),
) -> CropHistory:
    return service.advance_current_stage(db, owner, farm_id, data)
