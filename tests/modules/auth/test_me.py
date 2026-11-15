from fastapi.testclient import TestClient

CREDENCIALES = {
    "email": "perfil@example.com",
    "name": "Alguien",
    "password": "clave-larga-123",
    "role": "producer",
}


def test_sin_token_no_hay_acceso(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_con_token_valido_devuelve_el_perfil_propio(client: TestClient) -> None:
    client.post("/auth/register", json=CREDENCIALES)
    login = client.post(
        "/auth/login", json={"email": CREDENCIALES["email"], "password": CREDENCIALES["password"]}
    )
    access_token = login.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == CREDENCIALES["email"]
    assert "password" not in body


def test_token_invalido_devuelve_401(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer esto-no-es-un-jwt"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
