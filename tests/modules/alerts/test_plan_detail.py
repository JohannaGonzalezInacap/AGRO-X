from fastapi.testclient import TestClient

from app.integrations import forecast


def _trigger_frost(client, farm_id, headers, monkeypatch):
    def fake_forecast(latitude, longitude, days=7):
        return {"2026-11-16": {"t2m_max": 20.0, "t2m_min": -5.0, "precipitation_mm": 0.0}}

    monkeypatch.setattr(forecast, "get_daily_forecast", fake_forecast)
    return client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)


def test_plan_free_ve_solo_el_resumen(
    client: TestClient, seeded_crops, producer_with_farm, monkeypatch
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]

    response = _trigger_frost(client, farm_id, headers, monkeypatch)

    alert = response.json()[0]
    assert alert["type"] and alert["severity"] and alert["title"]
    assert alert["detail"] is None
    assert alert["recommendations"] is None


def test_plan_basico_ve_el_detalle(
    client: TestClient, seeded_crops, producer_with_farm, monkeypatch, set_plan
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    set_plan("alertas@example.com", "basic")

    response = _trigger_frost(client, farm_id, headers, monkeypatch)

    alert = response.json()[0]
    assert alert["detail"] is not None
    assert alert["recommendations"] is not None
