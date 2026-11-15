import uuid
from datetime import date, datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    """Plan free solo ve tipo, gravedad, título y fecha esperada (ADR-006); el resto de los campos
    queda en `None` para ese plan — ver `service._to_response`."""

    id: uuid.UUID
    type: str
    severity: str
    title: str
    expected_date: date | None
    detail: str | None
    recommendations: str | None
    suggested_crop: str | None
    illustrative: bool
    sources_used: list[str]
    created_at: datetime
