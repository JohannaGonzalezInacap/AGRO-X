from fastapi.testclient import TestClient

CREDENCIALES = {
    "email": "logout@example.com",
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


def test_logout_revoca_el_refresh_token(client: TestClient) -> None:
    tokens = _login(client)

    logout = client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout.status_code == 204

    refresh = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 401
