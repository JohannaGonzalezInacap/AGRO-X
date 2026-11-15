from fastapi.testclient import TestClient

PROFILE_PAYLOAD = {
    "business_name": "Verduras del Valle",
    "region": "Metropolitana",
    "products_of_interest": "tomate, lechuga",
}


def test_comerciante_crea_o_actualiza_su_perfil(
    client: TestClient, merchant_free_headers: dict
) -> None:
    response = client.put(
        "/marketplace/merchant-profile", json=PROFILE_PAYLOAD, headers=merchant_free_headers
    )

    assert response.status_code == 200
    assert response.json()["business_name"] == PROFILE_PAYLOAD["business_name"]


def test_un_productor_no_puede_tener_perfil_de_comerciante(
    client: TestClient, producer_free_headers: dict
) -> None:
    response = client.put(
        "/marketplace/merchant-profile", json=PROFILE_PAYLOAD, headers=producer_free_headers
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden"
