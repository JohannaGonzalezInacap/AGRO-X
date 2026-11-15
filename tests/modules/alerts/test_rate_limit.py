from fastapi.testclient import TestClient


def test_plan_free_solo_actualiza_una_vez_cada_30_dias(
    client: TestClient, seeded_crops, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]

    primera = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)
    assert primera.status_code == 200

    segunda = client.post(f"/farms/{farm_id}/alerts/refresh", headers=headers)

    assert segunda.status_code == 429
    body = segunda.json()["error"]
    assert body["code"] == "too_soon"
    assert "20" in body["message"]  # trae una fecha (año con "20...")
