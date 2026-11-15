from fastapi.testclient import TestClient


def test_productor_pro_lista_comerciantes(
    client: TestClient, producer_pro_headers: dict, merchant_free_headers: dict
) -> None:
    client.put(
        "/marketplace/merchant-profile",
        json={"business_name": "Verduras del Valle", "region": "Metropolitana"},
        headers=merchant_free_headers,
    )

    response = client.get("/marketplace/merchants", headers=producer_pro_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_productor_free_no_puede_listar_comerciantes(
    client: TestClient, producer_free_headers: dict
) -> None:
    response = client.get("/marketplace/merchants", headers=producer_free_headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "plan_required"
