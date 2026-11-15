import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.integrations import forecast, nasa_power
from app.modules.auth.models import User
from app.modules.rotation.models import Crop
from tests.modules.farms.conftest import FARM_PAYLOAD, register_and_login
from tests.modules.rotation.conftest import SEED_CROPS


@pytest.fixture
def set_plan(db_session):
    def _set_plan(email: str, plan: str) -> None:
        user = db_session.scalar(select(User).where(User.email == email))
        user.plan = plan
        db_session.commit()

    return _set_plan


@pytest.fixture
def seeded_crops(db_session) -> list[Crop]:
    crops = [Crop(source=None, **data) for data in SEED_CROPS]
    db_session.add_all(crops)
    db_session.commit()
    return crops


@pytest.fixture(autouse=True)
def _mock_mild_climate(monkeypatch):
    """Clima "tranquilo" por defecto: sin helada, calor, sequía ni lluvia intensa. Los tests que
    necesitan disparar una alerta sobreescriben esto con su propio monkeypatch. Regla 5 de
    fuentes-datos.md: nada de pruebas automáticas depende de internet."""

    def fake_forecast(latitude, longitude, days=7):
        return {
            f"2026-11-{15 + i:02d}": {
                "t2m_max": 20.0,
                "t2m_min": 10.0,
                "precipitation_mm": 3.0,
            }
            for i in range(min(days, 7))
        }

    def fake_observations(latitude, longitude, start, end):
        return {
            f"2026-11-{1 + i:02d}": {
                "t2m_max": 20.0,
                "t2m_min": 10.0,
                "precipitation_mm": 3.0,
                "soil_moisture": 0.4,
            }
            for i in range(7)
        }

    monkeypatch.setattr(forecast, "get_daily_forecast", fake_forecast)
    monkeypatch.setattr(nasa_power, "get_daily_observations", fake_observations)


@pytest.fixture
def producer_with_farm(client: TestClient) -> dict:
    headers = register_and_login(client, "alertas@example.com", role="producer")
    farm = client.post("/farms", json=FARM_PAYLOAD, headers=headers)
    return {"headers": headers, "farm_id": farm.json()["id"]}
