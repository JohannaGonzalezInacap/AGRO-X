import os

# Debe fijarse antes de importar cualquier módulo de la app: app.core.db llama a get_settings()
# al importarse. Una variable vacía en el .env local pisa el valor por defecto de Settings (no es
# "ausente", es un valor real para pydantic-settings) — ya pasó con JWT_SECRET y FORECAST_BASE_URL.
# Fijar esto aquí hace que las pruebas no dependan de que el .env local esté bien completado.
os.environ.setdefault("JWT_SECRET", "clave-de-pruebas-no-usar-en-produccion")
os.environ.setdefault("NASA_POWER_BASE_URL", "https://power.larc.nasa.gov")
os.environ.setdefault("FORECAST_BASE_URL", "https://api.open-meteo.com")
os.environ.setdefault("PAYMENT_WEBHOOK_SECRET", "secreto-de-pruebas-no-usar-en-produccion")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.core.rate_limit import login_rate_limiter
from app.main import app
from app.modules.auth import models as auth_models  # noqa: F401  (registra sus tablas en Base)


@pytest.fixture
def db_session():
    # StaticPool: una sola conexión compartida, para que la base en memoria sobreviva entre
    # sesiones dentro de la misma prueba (una conexión nueva de sqlite:///:memory: parte vacía).
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session) -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    login_rate_limiter.reset()
    try:
        # base_url="http://localhost": el host por defecto del TestClient ("testserver") no está
        # en ALLOWED_HOSTS, y el TrustedHostMiddleware lo rechazaría con 400 antes de llegar a la
        # ruta.
        yield TestClient(app, base_url="http://localhost", raise_server_exceptions=False)
    finally:
        app.dependency_overrides.pop(get_db, None)
