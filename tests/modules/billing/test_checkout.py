from fastapi.testclient import TestClient


def test_iniciar_un_pago_devuelve_direccion_de_pasarela(
    client: TestClient, producer_headers: dict
) -> None:
    response = client.post("/billing/checkout", json={"plan": "basic"}, headers=producer_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["checkout_url"]
    assert body["reference"]

    perfil = client.get("/auth/me", headers=producer_headers).json()
    assert perfil["plan"] == "free"  # mi plan sigue siendo el anterior.


def test_el_plan_no_cambia_al_solo_iniciar_el_pago_de_pro(
    client: TestClient, producer_headers: dict
) -> None:
    client.post("/billing/checkout", json={"plan": "pro"}, headers=producer_headers)

    perfil = client.get("/auth/me", headers=producer_headers).json()
    assert perfil["plan"] == "free"


def test_catalogo_de_planes_no_inventa_precio(client: TestClient) -> None:
    response = client.get("/billing/plans")

    assert response.status_code == 200
    planes = {p["id"]: p for p in response.json()}
    assert planes["free"]["price"] == 0
    assert planes["basic"]["price"] is None
    assert planes["basic"]["price_defined"] is False
    assert planes["pro"]["price"] is None
