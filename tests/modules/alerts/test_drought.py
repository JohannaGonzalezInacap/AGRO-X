from fastapi.testclient import TestClient

from app.integrations import forecast, nasa_power


def test_sequia_segun_observado_y_pronosticado(
    client: TestClient, seeded_crops, producer_with_farm, monkeypatch
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]

    def fake_observations(latitude, longitude, start, end):
        return {
            f"2026-11-{1 + i:02d}": {
                "t2m_max": 25.0, "t2m_min": 12.0, "precipitation_mm": 0.0, "soil_moisture": 0.1,
            }
            for i in range(7)
        }

    def fake_forecast(latitude, longitude, days=7):
        return {
            f"2026-11-{15 + i:02d}": {"t2m_max": 25.0, "t2m_min": 12.0, "precipitation_mm": 0.0}
            for i in range(7)
        }

    monkeypatch.setattr(nasa_power, "get_daily_observations", fake_observations)
    monkeypatch.setattr(forecast, "get_daily_forecast", fake_forecast)

    response = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    assert response.status_code == 200
    types = {a["type"] for a in response.json()}
    assert "drought" in types


def test_dato_faltante_no_se_toma_como_numero(
    client: TestClient, seeded_crops, producer_with_farm, monkeypatch
) -> None:
    """Un día con valor de relleno (None) no debe hacer que la sequía se detecte por error ni
    que se rompa el cálculo: se ignora ese día (spec/contratos/fuentes-datos.md)."""
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]

    def fake_observations(latitude, longitude, start, end):
        # Todos los días sin dato salvo uno con humedad alta: el promedio debe salir de ese
        # único día (0.8), no tratar los `None` como 0.
        data = {
            f"2026-11-{1 + i:02d}": {
                "t2m_max": None, "t2m_min": None, "precipitation_mm": None, "soil_moisture": None,
            }
            for i in range(6)
        }
        data["2026-11-07"] = {
            "t2m_max": 20.0, "t2m_min": 10.0, "precipitation_mm": 5.0, "soil_moisture": 0.8,
        }
        return data

    monkeypatch.setattr(nasa_power, "get_daily_observations", fake_observations)

    response = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    assert response.status_code == 200
    types = {a["type"] for a in response.json()}
    # Humedad real (del único día con dato) es alta -> no hay sequía.
    assert "drought" not in types
