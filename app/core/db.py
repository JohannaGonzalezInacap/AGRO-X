from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def normalize_database_url(url: str) -> str:
    """Varias plataformas (Render, Heroku y similares) entregan la URL de Postgres como
    `postgres://` o `postgresql://`, que SQLAlchemy resuelve con psycopg2 — pero este proyecto usa
    psycopg3 (`requirements.txt`). Sin este ajuste, el despliegue depende de qué texto exacto
    entregue cada proveedor (ADR-004: "cambiar de nube no obliga a reescribir código")."""

    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def _make_engine():
    settings = get_settings()
    url = normalize_database_url(settings.database_url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
