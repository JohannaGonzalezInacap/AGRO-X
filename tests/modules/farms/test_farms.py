from fastapi.testclient import TestClient

from tests.modules.farms.conftest import FARM_PAYLOAD, register_and_login


def test_crear_parcela_devuelve_201(client: TestClient, producer_headers: dict) -> None:
    response = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == FARM_PAYLOAD["name"]
    assert body["has_irrigation"] is False


def test_listar_devuelve_solo_mis_parcelas(client: TestClient, producer_headers: dict) -> None:
    client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)

    otros_headers = register_and_login(client, "otro-productor@example.com")
    client.post("/farms", json=FARM_PAYLOAD, headers=otros_headers)

    response = client.get("/farms", headers=producer_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_editar_y_borrar_parcela(client: TestClient, producer_headers: dict) -> None:
    creada = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
    farm_id = creada.json()["id"]

    editada = client.patch(
        f"/farms/{farm_id}", json={"area_hectares": 5.0}, headers=producer_headers
    )
    assert editada.status_code == 200
    assert editada.json()["area_hectares"] == 5.0

    borrada = client.delete(f"/farms/{farm_id}", headers=producer_headers)
    assert borrada.status_code == 204

    ya_no_existe = client.get(f"/farms/{farm_id}", headers=producer_headers)
    assert ya_no_existe.status_code == 404


def test_comerciante_no_puede_crear_parcelas(client: TestClient) -> None:
    merchant_headers = register_and_login(client, "comerciante@example.com", role="merchant")

    response = client.post("/farms", json=FARM_PAYLOAD, headers=merchant_headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden"


def test_sin_token_no_hay_acceso(client: TestClient) -> None:
    response = client.get("/farms")

    assert response.status_code == 401
