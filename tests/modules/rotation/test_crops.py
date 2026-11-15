from fastapi.testclient import TestClient

from tests.modules.farms.conftest import register_and_login


def test_catalogo_requiere_sesion(client: TestClient) -> None:
    response = client.get("/crops")

    assert response.status_code == 401


def test_catalogo_sin_fuente_sale_marcado_ilustrativo(client: TestClient, seeded_crops) -> None:
    headers = register_and_login(client, "cualquiera@example.com")

    response = client.get("/crops", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == len(seeded_crops)
    assert all(crop["illustrative"] is True for crop in body)
