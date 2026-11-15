import uuid
from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Farm(Base):
    """Parcela. Pertenece a un solo productor (dominio.md regla 1).

    `latitude`/`longitude`: la Fase 4 las redondea antes de enviarlas a fuentes externas
    (ver spec/contratos/fuentes-datos.md, regla 4) — aquí se guardan tal cual las ingresó el
    productor.
    """

    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    area_hectares: Mapped[float] = mapped_column(Float, nullable=False)
    soil_texture: Mapped[str | None] = mapped_column(String(100), nullable=True)
    drainage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    organic_matter_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    has_irrigation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    crop_history: Mapped[list["CropHistory"]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )


class CropHistory(Base):
    """Qué se sembró, cuándo y en qué etapa está (dominio.md).

    `current` (vigente): como máximo una fila en `True` por parcela (regla 10). Al registrar un
    cultivo nuevo, la fila vigente anterior pasa a `False` (regla 11); no se borra, queda como
    historial.
    """

    __tablename__ = "crop_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    crop: Mapped[str] = mapped_column(String(100), nullable=False)
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)
    stage: Mapped[str] = mapped_column(String(32), nullable=False)
    current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    farm: Mapped["Farm"] = relationship(back_populates="crop_history")
