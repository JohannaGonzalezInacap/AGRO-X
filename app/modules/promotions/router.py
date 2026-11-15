import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth.models import User
from app.modules.auth.service import require_role
from app.modules.promotions import service
from app.modules.promotions.schemas import PromotionIdeaResponse

router = APIRouter(prefix="/farms/{farm_id}/promotions", tags=["promotions"])

_require_producer = require_role("producer")


@router.get("/ideas", response_model=list[PromotionIdeaResponse])
def get_promotion_ideas(
    farm_id: uuid.UUID, owner: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> list[PromotionIdeaResponse]:
    return service.get_promotion_ideas(db, owner, farm_id)
