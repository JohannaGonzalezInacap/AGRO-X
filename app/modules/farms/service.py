import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.plans import max_farms_for
from app.modules.auth.models import User
from app.modules.farms.models import CropHistory, Farm
from app.modules.farms.schemas import (
    CropHistoryCreate,
    CropStageUpdate,
    FarmCreate,
    FarmUpdate,
)


def _not_found() -> AppError:
    # Misma respuesta si no existe o no es tuya (spec/contratos/api-v1.md).
    return AppError(404, "not_found", "No se encontró la parcela.")


def get_owned_farm_or_404(db: Session, owner: User, farm_id: uuid.UUID) -> Farm:
    farm = db.scalar(select(Farm).where(Farm.id == farm_id, Farm.owner_id == owner.id))
    if farm is None:
        raise _not_found()
    return farm


def list_farms(db: Session, owner: User) -> list[Farm]:
    return list(db.scalars(select(Farm).where(Farm.owner_id == owner.id).order_by(Farm.created_at)))


def create_farm(db: Session, owner: User, data: FarmCreate) -> Farm:
    count = len(list(db.scalars(select(Farm).where(Farm.owner_id == owner.id))))
    if count >= max_farms_for(owner):
        raise AppError(
            403,
            "plan_required",
            "Tu plan no permite registrar más parcelas. Sube de plan o borra una existente.",
        )

    farm = Farm(owner_id=owner.id, **data.model_dump())
    db.add(farm)
    db.commit()
    return farm


def update_farm(db: Session, owner: User, farm_id: uuid.UUID, data: FarmUpdate) -> Farm:
    farm = get_owned_farm_or_404(db, owner, farm_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(farm, field, value)
    db.commit()
    return farm


def delete_farm(db: Session, owner: User, farm_id: uuid.UUID) -> None:
    farm = get_owned_farm_or_404(db, owner, farm_id)
    db.delete(farm)
    db.commit()


def list_crop_history(db: Session, owner: User, farm_id: uuid.UUID) -> list[CropHistory]:
    get_owned_farm_or_404(db, owner, farm_id)
    return list(
        db.scalars(
            select(CropHistory)
            .where(CropHistory.farm_id == farm_id)
            .order_by(CropHistory.created_at.desc())
        )
    )


def register_crop(
    db: Session, owner: User, farm_id: uuid.UUID, data: CropHistoryCreate
) -> CropHistory:
    get_owned_farm_or_404(db, owner, farm_id)

    # Al registrar un cultivo nuevo, el vigente anterior deja de estarlo (dominio.md regla 11).
    db.query(CropHistory).filter(
        CropHistory.farm_id == farm_id, CropHistory.current.is_(True)
    ).update({"current": False})

    entry = CropHistory(
        farm_id=farm_id,
        crop=data.crop,
        planting_date=data.planting_date,
        stage=data.stage.value,
        current=True,
    )
    db.add(entry)
    db.commit()
    return entry


def advance_current_stage(
    db: Session, owner: User, farm_id: uuid.UUID, data: CropStageUpdate
) -> CropHistory:
    get_owned_farm_or_404(db, owner, farm_id)

    current = db.scalar(
        select(CropHistory).where(
            CropHistory.farm_id == farm_id, CropHistory.current.is_(True)
        )
    )
    if current is None:
        raise AppError(404, "not_found", "Esta parcela no tiene un cultivo vigente.")

    current.stage = data.stage.value
    db.commit()
    return current
