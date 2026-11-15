import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.alerts import service
from app.modules.alerts.schemas import AlertResponse
from app.modules.auth.models import User
from app.modules.auth.service import require_role

router = APIRouter(prefix="/farms/{farm_id}/alerts", tags=["alerts"])

_require_producer = require_role("producer")


@router.post("/refresh", response_model=list[AlertResponse])
def refresh_alerts(
    farm_id: uuid.UUID, owner: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> list[AlertResponse]:
    alerts = service.refresh_alerts(db, owner, farm_id)
    return [service.to_response(a, owner) for a in alerts]


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    farm_id: uuid.UUID, owner: User = Depends(_require_producer), db: Session = Depends(get_db)
) -> list[AlertResponse]:
    alerts = service.list_alerts(db, owner, farm_id)
    return [service.to_response(a, owner) for a in alerts]
