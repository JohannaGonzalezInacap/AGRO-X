from fastapi.testclient import TestClient

CREDENCIALES = {
    "email": "refresh@example.com",
    "name": "Alguien",
    "password": "clave-larga-123",
    "role": "producer",
}


def _login(client: TestClient) -> dict:
    client.post("/auth/register", json=CREDENCIALES)
    response = client.post(
        "/auth/login", json={"email": CREDENCIALES["email"], "password": CREDENCIALES["password"]}
    )
    return response.json()


def test_renovacion_normal_entrega_tokens_nuevos(client: TestClient) -> None:
    tokens = _login(client)

    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    nuevos = response.json()
    assert nuevos["refresh_token"] != tokens["refresh_token"]


def test_reutilizar_un_refresh_token_ya_usado_revoca_toda_la_cadena(client: TestClient) -> None:
    tokens = _login(client)

    primera = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert primera.status_code == 200
    token_nuevo = primera.json()["refresh_token"]

    # Reutilizar el token original (ya usado) debe fallar y revocar la familia completa.
    reuso = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reuso.status_code == 401
    assert reuso.json()["error"]["code"] == "invalid_refresh_token"

    # El token nuevo que se había entregado en la primera renovación también queda revocado.
    con_token_nuevo = client.post("/auth/refresh", json={"refresh_token": token_nuevo})
    assert con_token_nuevo.status_code == 401


def test_refresh_token_invalido_devuelve_401(client: TestClient) -> None:
    response = client.post("/auth/refresh", json={"refresh_token": "esto-no-existe"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_refresh_token"
