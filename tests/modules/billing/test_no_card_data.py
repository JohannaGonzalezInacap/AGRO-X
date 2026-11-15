from fastapi.testclient import TestClient


def test_ninguna_ruta_acepta_numero_de_tarjeta(client: TestClient, producer_headers: dict) -> None:
    response = client.post(
        "/billing/checkout",
        json={"plan": "basic", "card_number": "4111111111111111", "cvv": "123", "expiry": "12/30"},
        headers=producer_headers,
    )

    assert response.status_code == 422
