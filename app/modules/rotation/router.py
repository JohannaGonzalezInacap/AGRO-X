import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user, require_role
from app.modules.rotation import service
from app.modules.rotation.schemas import (
    CropResponse,
    RecommendationRequest,
    RecommendationResponse,
)

router = APIRouter(tags=["rotation"])

_require_producer = require_role("producer")


@router.get("/crops", response_model=list[CropResponse])
def list_crops(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[CropResponse]:
    return service.list_crops(db)


@router.post("/farms/{farm_id}/rotation/recommendations", response_model=RecommendationResponse)
def recommend_rotation(
    farm_id: uuid.UUID,
    request: RecommendationRequest,
    owner: User = Depends(_require_producer),
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    return service.recommend_rotation(db, owner, farm_id, request)
