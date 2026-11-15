from fastapi.testclient import TestClient

from app.integrations import nasa_power

SEED_CROPS_NAMES = {"maiz", "trigo", "papa", "poroto"}


def _registrar_cultivo(client, farm_id, headers, crop, stage="floracion"):
    return client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": crop, "planting_date": "2026-01-10", "stage": stage},
        headers=headers,
    )


def test_despues_de_maiz_la_leguminosa_puntua_mejor(
    client: TestClient, seeded_crops, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    _registrar_cultivo(client, farm_id, headers, "maiz")

    response = client.post(f"/farms/{farm_id}/rotation/recommendations", json={}, headers=headers)

    assert response.status_code == 200
    items = {item["crop"]: item for item in response.json()["items"]}
    assert items["poroto"]["score"] > items["trigo"]["score"]
    assert any("nitrógeno" in r for r in items["poroto"]["reasons"])


def test_se_evita_repetir_la_misma_familia(
    client: TestClient, seeded_crops, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    _registrar_cultivo(client, farm_id, headers, "maiz")
    _registrar_cultivo(client, farm_id, headers, "trigo")  # vigente; "maiz" queda como anterior

    response = client.post(f"/farms/{farm_id}/rotation/recommendations", json={}, headers=headers)

    items = {item["crop"]: item for item in response.json()["items"]}
    # "trigo" es el vigente, no se recomienda a sí mismo. "maiz" es de la misma familia
    # (gramineas) que los dos últimos del historial (maiz, trigo) y debe bajar de puntaje.
    assert "trigo" not in items
    assert any("plagas" in r or "enfermedades" in r for r in items["maiz"]["reasons"])
    assert items["maiz"]["score"] < items["poroto"]["score"]


def test_con_poca_agua_bajan_los_de_alta_demanda(
    client: TestClient, seeded_crops, producer_with_farm, monkeypatch
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]

    def fake_low_rain(latitude, longitude, start, end):
        return {str(start): {"precipitation_mm": 0.5, "t2m_max": 20, "t2m_min": 5, "soil_moisture": 0.2}}

    monkeypatch.setattr(nasa_power, "get_daily_observations", fake_low_rain)

    response = client.post(
        f"/farms/{farm_id}/rotation/recommendations",
        json={"priorities": ["water", "soil", "income"]},
        headers=headers,
    )

    items = {item["crop"]: item for item in response.json()["items"]}
    # "maiz" y "papa" tienen demanda de agua "alto"; "poroto" es "medio".
    assert items["maiz"]["score"] < items["poroto"]["score"]
    assert any("agua" in r for r in items["maiz"]["reasons"])


def test_toda_recomendacion_explica_sus_razones_y_sus_fuentes(
    client: TestClient, seeded_crops, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    _registrar_cultivo(client, farm_id, headers, "maiz")

    response = client.post(f"/farms/{farm_id}/rotation/recommendations", json={}, headers=headers)

    body = response.json()
    assert all(len(item["reasons"]) >= 1 for item in body["items"])
    assert "catalogo_cultivos" in body["sources_used"]
    assert "historial_de_parcela" in body["sources_used"]
    assert "nasa_power" in body["sources_used"]


def test_sin_historial_igual_hay_respuesta(
    client: TestClient, seeded_crops, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]

    response = client.post(f"/farms/{farm_id}/rotation/recommendations", json={}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == len(SEED_CROPS_NAMES)
    assert any("Sin historial" in n for n in body["notices"])


def test_valores_sin_fuente_se_marcan_ilustrativo(
    client: TestClient, seeded_crops, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]

    response = client.post(f"/farms/{farm_id}/rotation/recommendations", json={}, headers=headers)

    body = response.json()
    assert all(item["illustrative"] is True for item in body["items"])
