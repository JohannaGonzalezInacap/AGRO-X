from fastapi.testclient import TestClient

SURPLUS_PAYLOAD = {
    "product": "manzanas",
    "kilos": 200.0,
    "price": 50000,
    "region": "Metropolitana",
    "use": "alimento_animal",
}


def test_productor_pro_publica_una_merma(client: TestClient, producer_pro_headers: dict) -> None:
    response = client.post("/marketplace/surplus", json=SURPLUS_PAYLOAD, headers=producer_pro_headers)

    assert response.status_code == 201
    assert response.json()["product"] == "manzanas"


def test_productor_free_no_puede_publicar_mermas(
    client: TestClient, producer_free_headers: dict
) -> None:
    response = client.post("/marketplace/surplus", json=SURPLUS_PAYLOAD, headers=producer_free_headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "plan_required"


def test_contacto_no_se_ve_si_no_se_publico(
    client: TestClient, producer_pro_headers: dict, merchant_pro_headers: dict
) -> None:
    client.post(
        "/marketplace/surplus",
        json={**SURPLUS_PAYLOAD, "contact_visible": False, "contact": "+56912345678"},
        headers=producer_pro_headers,
    )

    response = client.get("/marketplace/surplus", headers=merchant_pro_headers)

    assert response.json()[0]["contact"] is None


def test_comerciante_pro_ve_el_contacto_si_se_publico(
    client: TestClient, producer_pro_headers: dict, merchant_pro_headers: dict
) -> None:
    client.post(
        "/marketplace/surplus",
        json={**SURPLUS_PAYLOAD, "contact_visible": True, "contact": "+56912345678"},
        headers=producer_pro_headers,
    )

    response = client.get("/marketplace/surplus", headers=merchant_pro_headers)

    assert response.json()[0]["contact"] == "+56912345678"


def test_comerciante_free_ve_la_merma_pero_no_el_contacto(
    client: TestClient, producer_pro_headers: dict, merchant_free_headers: dict
) -> None:
    client.post(
        "/marketplace/surplus",
        json={**SURPLUS_PAYLOAD, "contact_visible": True, "contact": "+56912345678"},
        headers=producer_pro_headers,
    )

    response = client.get("/marketplace/surplus", headers=merchant_free_headers)

    body = response.json()
    assert len(body) == 1
    assert body[0]["contact"] is None


def test_solo_el_dueno_cambia_el_estado_de_su_merma(
    client: TestClient, producer_pro_headers: dict, producer_free_headers: dict, set_plan
) -> None:
    set_plan("productor-free@example.com", "pro")
    creada = client.post("/marketplace/surplus", json=SURPLUS_PAYLOAD, headers=producer_pro_headers)
    surplus_id = creada.json()["id"]

    response = client.patch(
        f"/marketplace/surplus/{surplus_id}",
        json={"status": "reserved"},
        headers=producer_free_headers,
    )

    assert response.status_code == 404
