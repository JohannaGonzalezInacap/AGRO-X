from fastapi.testclient import TestClient


def test_ver_mis_consentimientos_antes_de_decidir_nada(
    client: TestClient, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]

    response = client.get("/privacy/consents", headers=headers)

    assert response.status_code == 200
    promo = response.json()["comunicaciones_promocionales"]
    assert promo["granted"] is False
    assert promo["updated_at"] is None


def test_otorgar_el_consentimiento_de_comunicaciones(
    client: TestClient, producer_with_farm
) -> None:
    headers = producer_with_farm["headers"]

    response = client.put(
        "/privacy/consents", json={"comunicaciones_promocionales": True}, headers=headers
    )

    assert response.status_code == 200
    promo = response.json()["comunicaciones_promocionales"]
    assert promo["granted"] is True
    assert promo["version"]
    assert promo["updated_at"] is not None


def test_retirarlo_es_tan_facil_como_darlo(client: TestClient, producer_with_farm) -> None:
    headers = producer_with_farm["headers"]
    client.put("/privacy/consents", json={"comunicaciones_promocionales": True}, headers=headers)

    response = client.put(
        "/privacy/consents", json={"comunicaciones_promocionales": False}, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["comunicaciones_promocionales"]["granted"] is False


def test_entrada_no_declarada_se_rechaza(client: TestClient, producer_with_farm) -> None:
    headers = producer_with_farm["headers"]

    response = client.put(
        "/privacy/consents",
        json={"comunicaciones_promocionales": True, "campo_extra": "no"},
        headers=headers,
    )

    assert response.status_code == 422
