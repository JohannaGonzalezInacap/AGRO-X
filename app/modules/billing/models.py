import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Payment(Base):
    """Intento de compra de un plan (dominio.md). Nunca guarda datos de tarjeta — solo lo que
    permite `spec/seguridad/pagos-pci.md` regla 3: plan, monto, moneda, estado, referencias."""

    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)  # en la unidad mínima de la moneda (CLP)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="CLP")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    reference: Mapped[uuid.UUID] = mapped_column(unique=True, default=uuid.uuid4, nullable=False)
    gateway_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class WebhookEvent(Base):
    """Un aviso ya procesado no se vuelve a aplicar (spec/bdd/pagos.feature, "Aviso repetido")."""

    __tablename__ = "webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    external_event_id: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    __table_args__ = (UniqueConstraint("provider", "external_event_id"),)
