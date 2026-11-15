import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.errors import AppError
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.billing import service
from app.modules.billing.models import Payment
from app.modules.billing.providers import fake as fake_provider
from app.modules.billing.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    FakeApproveRequest,
    PlanResponse,
    SubscriptionResponse,
)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanResponse])
def list_plans() -> list[PlanResponse]:
    return service.get_plan_catalog()


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    data: CheckoutRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CheckoutResponse:
    return service.start_checkout(db, user, data)


@router.get("/subscription", response_model=SubscriptionResponse)
def subscription(user: User = Depends(get_current_user)) -> User:
    return service.get_subscription(user)


@router.post("/webhooks/{provider}", status_code=status.HTTP_200_OK)
async def webhook(provider: str, request: Request, db: Session = Depends(get_db)) -> dict:
    body = await request.body()
    headers = dict(request.headers)
    query_params = dict(request.query_params)
    service.handle_webhook(db, request, provider, headers, query_params, body)
    return {"status": "ok"}


@router.post("/_dev/fake-approve/{reference}", status_code=status.HTTP_204_NO_CONTENT)
def fake_approve(reference: uuid.UUID, data: FakeApproveRequest, db: Session = Depends(get_db)) -> None:
    """Solo para desarrollo: simula el resultado que la pasarela 'fake' daría al confirmar un
    pago. Nunca disponible si la pasarela configurada no es 'fake' (ADR-003: prohibida en
    producción)."""
    settings = get_settings()
    if settings.payment_provider != "fake":
        raise AppError(404, "not_found", "No encontrado.")

    payment = db.scalar(select(Payment).where(Payment.reference == reference))
    if payment is None:
        raise AppError(404, "not_found", "No se encontró ese pago.")

    fake_provider.simulate_result(
        str(reference),
        data.status,
        data.amount if data.amount is not None else payment.amount,
        data.currency if data.currency is not None else payment.currency,
    )
