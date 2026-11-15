import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.integrations import forecast, nasa_power
from app.modules.auth.models import User
from tests.modules.farms.conftest import FARM_PAYLOAD, register_and_login


@pytest.fixture
def set_plan(db_session):
    def _set_plan(email: str, plan: str) -> None:
        user = db_session.scalar(select(User).where(User.email == email))
        user.plan = plan
        db_session.commit()

    return _set_plan


@pytest.fixture(autouse=True)
def _mock_mild_climate(monkeypatch):
    """Clima "tranquilo" por defecto, igual que en tests/modules/alerts/conftest.py: sin helada,
    calor, sequía ni lluvia intensa salvo que el test lo sobreescriba."""

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
    headers = register_and_login(client, "promociones@example.com", role="producer")
    farm = client.post("/farms", json=FARM_PAYLOAD, headers=headers)
    return {"headers": headers, "farm_id": farm.json()["id"]}


def trigger_high_severity_alert(client: TestClient, farm_id: str, headers: dict, monkeypatch) -> None:
    """Helada bien por debajo del umbral: severidad "alta" (igual criterio que
    tests/modules/alerts/test_plan_detail.py)."""

    def fake_forecast(latitude, longitude, days=7):
        return {"2026-11-16": {"t2m_max": 20.0, "t2m_min": -5.0, "precipitation_mm": 0.0}}

    monkeypatch.setattr(forecast, "get_daily_forecast", fake_forecast)
    client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)


def trigger_medium_severity_alert(client: TestClient, farm_id: str, headers: dict, monkeypatch) -> None:
    """Sequía: el motor de riesgo siempre la marca con severidad "media" (ver
    app/modules/alerts/service.py, _evaluate_drought)."""

    def fake_observations(latitude, longitude, start, end):
        return {
            "2026-11-01": {
                "t2m_max": 20.0,
                "t2m_min": 10.0,
                "precipitation_mm": 0.0,
                "soil_moisture": 0.05,
            }
        }

    def fake_forecast_no_rain(latitude, longitude, days=7):
        return {
            f"2026-11-{15 + i:02d}": {"t2m_max": 20.0, "t2m_min": 10.0, "precipitation_mm": 0.0}
            for i in range(min(days, 7))
        }

    monkeypatch.setattr(nasa_power, "get_daily_observations", fake_observations)
    monkeypatch.setattr(forecast, "get_daily_forecast", fake_forecast_no_rain)
    client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)
