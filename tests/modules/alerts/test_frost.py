from fastapi.testclient import TestClient

from app.integrations import forecast


def test_helada_pronosticada_crea_alerta_de_tipo_frost(
    client: TestClient, seeded_crops, producer_with_farm, monkeypatch
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    # "maiz" tiene frost_tolerance "baja" -> umbral 2 °C (ADR-011).
    client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": "maiz", "planting_date": "2026-01-10", "stage": "floracion"},
        headers=headers,
    )

    def fake_forecast(latitude, longitude, days=7):
        return {
            "2026-11-16": {"t2m_max": 20.0, "t2m_min": 10.0, "precipitation_mm": 3.0},
            "2026-11-17": {"t2m_max": 18.0, "t2m_min": 1.0, "precipitation_mm": 3.0},
        }

    monkeypatch.setattr(forecast, "get_daily_forecast", fake_forecast)

    response = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    assert response.status_code == 200
    alerts = {a["type"]: a for a in response.json()}
    assert alerts["frost"]["expected_date"] == "2026-11-17"
