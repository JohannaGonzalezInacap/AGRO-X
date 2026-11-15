from fastapi.testclient import TestClient


def test_registro_como_productor_devuelve_201_con_perfil_sin_contrasena(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "productora@example.com",
            "name": "Productora Uno",
            "password": "clave-larga-123",
            "role": "producer",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "productora@example.com"
    assert body["role"] == "producer"
    assert body["plan"] == "free"
    assert "password" not in body
    assert "password_hash" not in body


def test_no_se_puede_registrar_como_administrador(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "nuevo@example.com",
            "name": "Alguien",
            "password": "clave-larga-123",
            "role": "admin",
        },
    )

    assert response.status_code == 422


def test_no_se_pueden_enviar_campos_extra(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "nuevo@example.com",
            "name": "Alguien",
            "password": "clave-larga-123",
            "role": "producer",
            "plan": "pro",
        },
    )

    assert response.status_code == 422


def test_correo_duplicado_devuelve_409(client: TestClient) -> None:
    payload = {
        "email": "repetido@example.com",
        "name": "Alguien",
        "password": "clave-larga-123",
        "role": "producer",
    }

    primero = client.post("/auth/register", json=payload)
    segundo = client.post("/auth/register", json=payload)

    assert primero.status_code == 201
    assert segundo.status_code == 409
    assert segundo.json()["error"]["code"] == "email_taken"
