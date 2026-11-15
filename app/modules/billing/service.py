import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.modules.auth.models import AuditLog, User
from app.modules.billing.models import Payment, WebhookEvent
from app.modules.billing.providers.base import BillingProvider
from app.modules.billing.providers.fake import FakeBillingProvider
from app.modules.billing.providers.mercadopago import MercadoPagoProvider
from app.modules.billing.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    PlanResponse,
    PurchasablePlan,
)

# ADR-012: precio de desarrollo, no es el precio real (todavía "Por definir" en
# spec/alcance-y-planes.md). Nunca se expone en GET /billing/plans como si fuera definitivo.
_DEV_PRICES = {PurchasablePlan.BASIC: 9990, PurchasablePlan.PRO: 19990}
_CURRENCY = "CLP"
_SUBSCRIPTION_DAYS = 30

_PROVIDERS: dict[str, type[BillingProvider]] = {
    "fake": FakeBillingProvider,
    "mercadopago": MercadoPagoProvider,
}


def get_provider(name: str) -> BillingProvider:
    provider_cls = _PROVIDERS.get(name)
    if provider_cls is None:
        raise AppError(404, "not_found", "Pasarela de pago no reconocida.")
    return provider_cls()


def get_plan_catalog() -> list[PlanResponse]:
    return [
        PlanResponse(id="free", name="Free", price=0, currency=_CURRENCY, price_defined=True),
        PlanResponse(id="basic", name="Básico", price=None, currency=_CURRENCY, price_defined=False),
        PlanResponse(id="pro", name="Pro", price=None, currency=_CURRENCY, price_defined=False),
    ]


def start_checkout(db: Session, user: User, data: CheckoutRequest) -> CheckoutResponse:
    settings = get_settings()
    provider = get_provider(settings.payment_provider)
    amount = _DEV_PRICES[data.plan]

    payment = Payment(
        user_id=user.id,
        plan=data.plan.value,
        amount=amount,
        currency=_CURRENCY,
        status="pending",
        provider=settings.payment_provider,
    )
    db.add(payment)
    db.flush()  # para tener payment.reference antes de pedirle la URL al proveedor

    checkout_url = provider.create_checkout(payment)
    db.commit()
    return CheckoutResponse(checkout_url=checkout_url, reference=str(payment.reference))


def _audit(db: Session, request: Request, user_id: uuid.UUID | None, action: str) -> None:
    request_id = getattr(request.state, "request_id", "unknown")
    db.add(AuditLog(user_id=user_id, action=action, request_id=request_id))


def handle_webhook(
    db: Session,
    request: Request,
    provider_name: str,
    headers: dict,
    query_params: dict,
    body: bytes,
) -> None:
    provider = get_provider(provider_name)

    if not provider.verify_signature(headers, query_params, body):
        raise AppError(401, "unauthorized", "Firma del aviso inválida.")

    event_id = provider.extract_event_id(headers, query_params, body)
    if event_id and db.scalar(
        select(WebhookEvent).where(
            WebhookEvent.provider == provider_name, WebhookEvent.external_event_id == event_id
        )
    ):
        return  # aviso ya procesado: 200, sin reaplicar nada (spec/bdd/pagos.feature).

    gateway_payment_id = provider.extract_gateway_payment_id(headers, query_params, body)
    confirmation = provider.confirm_payment(gateway_payment_id)  # puede lanzar 502; no se marca
    # como procesado si falla aquí, para que un reintento legítimo sí se vuelva a evaluar.

    payment = None
    if confirmation.external_reference:
        try:
            payment = db.scalar(
                select(Payment).where(Payment.reference == uuid.UUID(confirmation.external_reference))
            )
        except ValueError:
            payment = None
    if payment is None:
        raise AppError(422, "validation_error", "Referencia de pago desconocida.")

    if confirmation.status == "approved" and (
        confirmation.amount != payment.amount or confirmation.currency != payment.currency
    ):
        payment.status = "amount_mismatch"
        _audit(db, request, payment.user_id, "payment_amount_mismatch")
    elif confirmation.status == "approved":
        payment.status = "approved"
        payment.gateway_payment_id = confirmation.gateway_payment_id
        user = db.get(User, payment.user_id)
        user.plan = payment.plan
        user.plan_valid_until = datetime.now(UTC) + timedelta(days=_SUBSCRIPTION_DAYS)
        _audit(db, request, payment.user_id, "payment_approved")
    else:
        payment.status = confirmation.status
        _audit(db, request, payment.user_id, "payment_rejected")

    if event_id:
        db.add(WebhookEvent(provider=provider_name, external_event_id=event_id))
    db.commit()


def get_subscription(user: User) -> User:
    return user
