import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Crop(Base):
    """Ficha agronómica del catálogo (dominio.md). `source` es la fuente agronómica: si es `None`,
    la respuesta de la recomendación marca ese dato como ilustrativo (RUTA.md, Fase 5)."""

    __tablename__ = "crops"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    family: Mapped[str] = mapped_column(String(100), nullable=False)
    water_need: Mapped[str] = mapped_column(String(16), nullable=False)  # bajo | medio | alto
    nitrogen_effect: Mapped[str] = mapped_column(String(16), nullable=False)  # fija | consume | neutro
    root_depth: Mapped[str] = mapped_column(String(16), nullable=False)  # superficial | profunda
    frost_tolerance: Mapped[str] = mapped_column(String(16), nullable=False)  # baja | media | alta
    heat_tolerance: Mapped[str] = mapped_column(String(16), nullable=False)  # baja | media | alta
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
