import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Consent(Base):
    """Un consentimiento puntual (ADR-014, ND-003). Por ahora solo existe el tipo
    "comunicaciones_promocionales" — los otros dos de `spec/privacidad/derechos-y-consentimiento.md`
    ya los gobierna `app/modules/marketplace/` y no se duplican aquí.

    `version`: el texto que la persona aceptó (dominio.md regla de consentimientos, "fecha y
    versión del texto aceptado").
    """

    __tablename__ = "consents"
    __table_args__ = (UniqueConstraint("user_id", "kind"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[str] = mapped_column(String(16), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
