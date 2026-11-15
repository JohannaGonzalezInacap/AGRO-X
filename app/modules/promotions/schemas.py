import uuid

from pydantic import BaseModel


class PromotionIdeaResponse(BaseModel):
    """Ideas de venta urgente para una alerta puntual de severidad alta (ADR-013).

    Son ilustrativas (`illustrative: true`): no hay todavía una fuente real de precios o canales
    de venta, solo sugerencias armadas a partir del tipo de alerta y el cultivo vigente.
    """

    alert_id: uuid.UUID
    alert_type: str
    alert_title: str
    crop: str | None
    ideas: list[str]
    illustrative: bool
    sources_used: list[str]
