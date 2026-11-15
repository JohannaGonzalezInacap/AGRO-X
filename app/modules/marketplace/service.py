import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import plans
from app.core.errors import AppError
from app.modules.auth.models import User
from app.modules.marketplace.models import MerchantProfile, Surplus
from app.modules.marketplace.schemas import (
    MerchantProfileUpsert,
    SurplusCreate,
    SurplusResponse,
    SurplusStatusUpdate,
)


def upsert_merchant_profile(
    db: Session, merchant: User, data: MerchantProfileUpsert
) -> MerchantProfile:
    profile = db.scalar(select(MerchantProfile).where(MerchantProfile.user_id == merchant.id))
    if profile is None:
        profile = MerchantProfile(user_id=merchant.id)
        db.add(profile)
    profile.business_name = data.business_name
    profile.region = data.region
    profile.products_of_interest = data.products_of_interest
    profile.contact = data.contact
    db.commit()
    return profile


def _require_marketplace_access(producer: User) -> None:
    if not plans.marketplace_access_allowed(producer):
        raise AppError(
            403, "plan_required", "Esta función requiere el plan pro."
        )


def list_merchants(db: Session, producer: User) -> list[MerchantProfile]:
    _require_marketplace_access(producer)
    return list(db.scalars(select(MerchantProfile).order_by(MerchantProfile.business_name)))


def create_surplus(db: Session, producer: User, data: SurplusCreate) -> Surplus:
    _require_marketplace_access(producer)
    surplus = Surplus(producer_id=producer.id, **data.model_dump())
    db.add(surplus)
    db.commit()
    return surplus


def _visible_contact(surplus: Surplus, viewer: User) -> str | None:
    if not surplus.contact_visible:
        return None
    if not plans.merchant_contact_visibility_allowed(viewer):  # ND-001
        return None
    return surplus.contact


def to_response(surplus: Surplus, viewer: User) -> SurplusResponse:
    is_owner = surplus.producer_id == viewer.id
    contact = surplus.contact if is_owner else _visible_contact(surplus, viewer)
    return SurplusResponse(
        id=surplus.id,
        product=surplus.product,
        kilos=surplus.kilos,
        price=surplus.price,
        region=surplus.region,
        use=surplus.use,
        status=surplus.status,
        contact=contact,
        created_at=surplus.created_at,
    )


def list_surplus(db: Session, user: User) -> list[Surplus]:
    if user.role == "producer":
        return list(
            db.scalars(
                select(Surplus).where(Surplus.producer_id == user.id).order_by(Surplus.created_at.desc())
            )
        )
    return list(db.scalars(select(Surplus).order_by(Surplus.created_at.desc())))


def update_surplus_status(
    db: Session, producer: User, surplus_id: uuid.UUID, data: SurplusStatusUpdate
) -> Surplus:
    surplus = db.scalar(
        select(Surplus).where(Surplus.id == surplus_id, Surplus.producer_id == producer.id)
    )
    if surplus is None:
        raise AppError(404, "not_found", "No se encontró la merma.")
    surplus.status = data.status.value
    db.commit()
    return surplus
