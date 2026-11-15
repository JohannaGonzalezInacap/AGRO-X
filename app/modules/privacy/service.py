import uuid
from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.alerts.models import Alert
from app.modules.auth.models import AuditLog, User
from app.modules.auth.schemas import UserProfileResponse
from app.modules.billing.models import Payment
from app.modules.farms.models import CropHistory, Farm
from app.modules.marketplace.models import MerchantProfile, Surplus
from app.modules.privacy.models import Consent
from app.modules.privacy.schemas import (
    PROMOTIONAL_COMMS_KIND,
    AlertExport,
    ConsentExport,
    ConsentsResponse,
    ConsentsUpdate,
    CropHistoryExport,
    DataExportResponse,
    FarmExport,
    MerchantProfileExport,
    PaymentExport,
    SurplusExport,
)

_CONSENT_VERSION = "1.0"


def _audit(db: Session, request: Request, user_id: uuid.UUID | None, action: str) -> None:
    request_id = getattr(request.state, "request_id", "unknown")
    db.add(AuditLog(user_id=user_id, action=action, request_id=request_id))


def _export_farms(db: Session, owner: User) -> list[FarmExport]:
    farms = list(db.scalars(select(Farm).where(Farm.owner_id == owner.id).order_by(Farm.created_at)))
    exported = []
    for farm in farms:
        crop_history = db.scalars(
            select(CropHistory).where(CropHistory.farm_id == farm.id).order_by(CropHistory.created_at.desc())
        )
        alerts = db.scalars(select(Alert).where(Alert.farm_id == farm.id).order_by(Alert.created_at.desc()))
        exported.append(
            FarmExport(
                id=farm.id,
                name=farm.name,
                region=farm.region,
                latitude=farm.latitude,
                longitude=farm.longitude,
                area_hectares=farm.area_hectares,
                soil_texture=farm.soil_texture,
                drainage=farm.drainage,
                organic_matter_percent=farm.organic_matter_percent,
                has_irrigation=farm.has_irrigation,
                crop_history=[CropHistoryExport.model_validate(c) for c in crop_history],
                alerts=[AlertExport.model_validate(a) for a in alerts],
            )
        )
    return exported


def _get_consent_row(db: Session, user_id: uuid.UUID) -> Consent | None:
    return db.scalar(
        select(Consent).where(Consent.user_id == user_id, Consent.kind == PROMOTIONAL_COMMS_KIND)
    )


def get_consents(db: Session, user: User) -> ConsentsResponse:
    row = _get_consent_row(db, user.id)
    promo = ConsentExport(
        kind=PROMOTIONAL_COMMS_KIND,
        granted=row.granted if row else False,
        version=row.version if row else _CONSENT_VERSION,
        updated_at=row.updated_at if row else None,
    )
    return ConsentsResponse(comunicaciones_promocionales=promo)


def update_consents(
    db: Session, user: User, request: Request, data: ConsentsUpdate
) -> ConsentsResponse:
    row = _get_consent_row(db, user.id)
    if row is None:
        row = Consent(
            user_id=user.id,
            kind=PROMOTIONAL_COMMS_KIND,
            granted=data.comunicaciones_promocionales,
            version=_CONSENT_VERSION,
        )
        db.add(row)
    else:
        row.granted = data.comunicaciones_promocionales
        row.version = _CONSENT_VERSION
    _audit(db, request, user.id, "consent_updated")
    db.commit()
    return get_consents(db, user)


def get_data_export(db: Session, user: User, request: Request) -> DataExportResponse:
    merchant_profile = None
    if user.role == "merchant":
        profile = db.scalar(select(MerchantProfile).where(MerchantProfile.user_id == user.id))
        if profile is not None:
            merchant_profile = MerchantProfileExport.model_validate(profile)

    surplus_export: list[SurplusExport] = []
    if user.role == "producer":
        rows = db.scalars(
            select(Surplus).where(Surplus.producer_id == user.id).order_by(Surplus.created_at.desc())
        )
        surplus_export = [SurplusExport.model_validate(r) for r in rows]

    payments = db.scalars(
        select(Payment).where(Payment.user_id == user.id).order_by(Payment.created_at.desc())
    )
    payments_export = [PaymentExport.model_validate(p) for p in payments]

    export = DataExportResponse(
        exported_at=datetime.now(UTC),
        account=UserProfileResponse.model_validate(user),
        farms=_export_farms(db, user),
        merchant_profile=merchant_profile,
        surplus=surplus_export,
        payments=payments_export,
        consents=get_consents(db, user),
    )

    _audit(db, request, user.id, "privacy_export")
    db.commit()
    return export


def delete_account(db: Session, user: User, request: Request) -> None:
    """Borra lo propio; anonimiza (no borra) pagos y auditoría (ADR-014,
    spec/privacidad/retencion-y-borrado.md)."""

    farms = list(db.scalars(select(Farm).where(Farm.owner_id == user.id)))
    farm_ids = [farm.id for farm in farms]
    if farm_ids:
        db.query(Alert).filter(Alert.farm_id.in_(farm_ids)).delete(synchronize_session=False)
    for farm in farms:
        db.delete(farm)  # cascada a su historial de cultivo (app/modules/farms/models.py)

    db.query(MerchantProfile).filter(MerchantProfile.user_id == user.id).delete(
        synchronize_session=False
    )
    db.query(Surplus).filter(Surplus.producer_id == user.id).delete(synchronize_session=False)
    db.query(Consent).filter(Consent.user_id == user.id).delete(synchronize_session=False)

    db.query(Payment).filter(Payment.user_id == user.id).update(
        {"user_id": None}, synchronize_session=False
    )
    db.query(AuditLog).filter(AuditLog.user_id == user.id).update(
        {"user_id": None}, synchronize_session=False
    )

    _audit(db, request, None, "account_deleted")
    db.delete(user)  # cascada a sus tokens de renovación (app/modules/auth/models.py)
    db.commit()
