from fastapi.testclient import TestClient

from tests.modules.farms.conftest import FARM_PAYLOAD, register_and_login


def test_un_usuario_no_ve_la_parcela_de_otro(client: TestClient, producer_headers: dict) -> None:
    creada = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
    farm_id = creada.json()["id"]

    otro_headers = register_and_login(client, "otro@example.com")

    response = client.get(f"/farms/{farm_id}", headers=otro_headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_un_usuario_no_puede_editar_la_parcela_de_otro(
    client: TestClient, producer_headers: dict
) -> None:
    creada = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
    farm_id = creada.json()["id"]

    otro_headers = register_and_login(client, "otro2@example.com")

    response = client.patch(f"/farms/{farm_id}", json={"area_hectares": 9.0}, headers=otro_headers)

    assert response.status_code == 404


def test_un_usuario_no_puede_borrar_la_parcela_de_otro(
    client: TestClient, producer_headers: dict
) -> None:
    creada = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
    farm_id = creada.json()["id"]

    otro_headers = register_and_login(client, "otro3@example.com")

    response = client.delete(f"/farms/{farm_id}", headers=otro_headers)

    assert response.status_code == 404
