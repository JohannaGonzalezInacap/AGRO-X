import uuid
from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Alert(Base):
    """Riesgo climático o aviso de cambio de cultivo para una parcela (dominio.md).

    `active`: una alerta que ya no aplica al recalcular no se borra, queda como historial con
    `active=False` (mismo criterio que el historial de cultivos, Fase 3).
    """

    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farms.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    illustrative: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sources_used: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
