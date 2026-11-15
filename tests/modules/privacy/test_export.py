import json

from fastapi.testclient import TestClient


def test_exportar_mis_datos_entrega_mi_informacion(
    client: TestClient, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": "maiz", "planting_date": "2026-01-10", "stage": "crecimiento"},
        headers=headers,
    )

    response = client.get("/privacy/export", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["account"]["email"] == "privacidad@example.com"
    assert len(body["farms"]) == 1
    assert body["farms"][0]["id"] == farm_id
    assert body["farms"][0]["crop_history"][0]["crop"] == "maiz"


def test_la_exportacion_no_incluye_contrasenas_ni_tokens(
    client: TestClient, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]

    response = client.get("/privacy/export", headers=headers)

    body_text = json.dumps(response.json())
    assert "clave-larga-123" not in body_text
    assert "password" not in body_text
    assert "token" not in body_text
