from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class PlanId(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"


class PurchasablePlan(str, Enum):
    """Free no se compra; no tiene sentido iniciar un pago para él."""

    BASIC = "basic"
    PRO = "pro"


class PlanResponse(BaseModel):
    id: str
    name: str
    # Básico y pro: spec/alcance-y-planes.md dice "Por definir". No se inventa un número: queda
    # en None hasta que el equipo lo fije.
    price: int | None
    currency: str
    price_defined: bool


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan: PurchasablePlan


class CheckoutResponse(BaseModel):
    checkout_url: str
    reference: str


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan: str
    plan_valid_until: datetime | None


class FakeApproveRequest(BaseModel):
    """Solo para el endpoint de desarrollo (POST /billing/_dev/fake-approve/{referencia})."""

    model_config = ConfigDict(extra="forbid")

    status: str = "approved"
    amount: int | None = None
    currency: str | None = None
