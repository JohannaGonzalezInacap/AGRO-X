import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class MerchantProfile(Base):
    """Datos del negocio comprador (dominio.md). Un comerciante tiene a lo más uno."""

    __tablename__ = "merchant_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False, index=True
    )
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    products_of_interest: Mapped[str] = mapped_column(Text, nullable=False, default="")
    contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


class Surplus(Base):
    """Merma: producto no apto para venta normal (dominio.md regla 7: el contacto solo se
    muestra si `contact_visible` es verdadero, y además solo a un comerciante pro, ND-001)."""

    __tablename__ = "surplus"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    producer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    product: Mapped[str] = mapped_column(String(100), nullable=False)
    kilos: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    use: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="available")
    contact_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
