import pytest
from fastapi.testclient import TestClient

from app.integrations import nasa_power
from app.modules.rotation.models import Crop
from tests.modules.farms.conftest import FARM_PAYLOAD, register_and_login

SEED_CROPS = [
    {
        "name": "maiz", "family": "gramineas", "water_need": "alto", "nitrogen_effect": "consume",
        "root_depth": "profunda", "frost_tolerance": "baja", "heat_tolerance": "alta",
    },
    {
        "name": "trigo", "family": "gramineas", "water_need": "medio", "nitrogen_effect": "consume",
        "root_depth": "profunda", "frost_tolerance": "media", "heat_tolerance": "media",
    },
    {
        "name": "papa", "family": "solanaceas", "water_need": "alto", "nitrogen_effect": "consume",
        "root_depth": "superficial", "frost_tolerance": "baja", "heat_tolerance": "media",
    },
    {
        "name": "poroto", "family": "leguminosas", "water_need": "medio", "nitrogen_effect": "fija",
        "root_depth": "superficial", "frost_tolerance": "baja", "heat_tolerance": "media",
    },
]


@pytest.fixture
def seeded_crops(db_session) -> list[Crop]:
    crops = [Crop(source=None, **data) for data in SEED_CROPS]
    db_session.add_all(crops)
    db_session.commit()
    return crops


@pytest.fixture(autouse=True)
def _mock_moderate_rain(monkeypatch):
    """Por defecto, lluvia moderada (sin "baja precipitación"). Rule 5 de fuentes-datos.md: nada
    de pruebas automáticas depende de internet."""

    def fake_observations(latitude, longitude, start, end):
        return {
            str(start): {
                "t2m_max": 20.0,
                "t2m_min": 8.0,
                "precipitation_mm": 5.0,
                "soil_moisture": 0.4,
            }
        }

    monkeypatch.setattr(nasa_power, "get_daily_observations", fake_observations)


@pytest.fixture
def producer_with_farm(client: TestClient) -> dict:
    headers = register_and_login(client, "rotacion@example.com", role="producer")
    farm = client.post("/farms", json=FARM_PAYLOAD, headers=headers)
    return {"headers": headers, "farm_id": farm.json()["id"]}
