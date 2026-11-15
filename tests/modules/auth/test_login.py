from fastapi.testclient import TestClient

CREDENCIALES = {
    "email": "login@example.com",
    "name": "Alguien",
    "password": "clave-larga-123",
    "role": "producer",
}


def _registrar(client: TestClient) -> None:
    response = client.post("/auth/register", json=CREDENCIALES)
    assert response.status_code == 201


def test_login_correcto_devuelve_tokens(client: TestClient) -> None:
    _registrar(client)

    response = client.post(
        "/auth/login", json={"email": CREDENCIALES["email"], "password": CREDENCIALES["password"]}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


def test_correo_inexistente_devuelve_401_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/auth/login", json={"email": "no-existe@example.com", "password": "lo-que-sea-123"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_contrasena_incorrecta_devuelve_401_invalid_credentials(client: TestClient) -> None:
    _registrar(client)

    response = client.post(
        "/auth/login", json={"email": CREDENCIALES["email"], "password": "contrasena-mala-123"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"
