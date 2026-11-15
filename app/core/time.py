from datetime import UTC, datetime


def as_aware_utc(value: datetime) -> datetime:
    """SQLite no conserva el huso horario aunque la columna sea `DateTime(timezone=True)`: al leer
    vuelve "naive". PostgreSQL sí lo conserva. Se normaliza aquí para poder comparar siempre con un
    datetime "aware" (ver spec/adr/ADR-001-stack.md: SQLite solo se usa en pruebas)."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
