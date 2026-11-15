from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_supera_el_limite_de_intentos_de_login(client: TestClient) -> None:
    limite = get_settings().login_rate_limit_attempts

    for _ in range(limite):
        response = client.post(
            "/auth/login", json={"email": "no-existe@example.com", "password": "lo-que-sea-123"}
        )
        assert response.status_code == 401

    bloqueado = client.post(
        "/auth/login", json={"email": "no-existe@example.com", "password": "lo-que-sea-123"}
    )

    assert bloqueado.status_code == 429
    assert bloqueado.json()["error"]["code"] == "rate_limited"
