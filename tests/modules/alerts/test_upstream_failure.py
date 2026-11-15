import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.errors import AppError
from app.integrations import forecast
from app.modules.farms.models import Farm


def test_falla_la_fuente_externa_devuelve_502_y_conserva_alertas_anteriores(
    client: TestClient, seeded_crops, producer_with_farm, monkeypatch, db_session
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]

    primera = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)
    assert primera.status_code == 200
    alertas_anteriores = client.get(f"/farms/{farm_id}/alerts", headers=headers).json()

    # Para probar la segunda llamada sin esperar el límite de intentos por plan (eso ya lo
    # cubre test_rate_limit.py), se libera el recálculo directamente en la base de la prueba.
    farm = db_session.scalar(select(Farm).where(Farm.id == uuid.UUID(farm_id)))
    farm.alerts_refreshed_at = None
    db_session.commit()

    def fake_forecast_falla(latitude, longitude, days=7):
        raise AppError(502, "upstream_unavailable", "La fuente de pronóstico no respondió.")

    monkeypatch.setattr(forecast, "get_daily_forecast", fake_forecast_falla)

    response = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "upstream_unavailable"

    siguen_disponibles = client.get(f"/farms/{farm_id}/alerts", headers=headers).json()
    assert siguen_disponibles == alertas_anteriores
