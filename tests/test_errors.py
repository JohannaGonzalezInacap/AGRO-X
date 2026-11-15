from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.errors import register_error_handlers


def test_ruta_inexistente_devuelve_formato_unico(client: TestClient) -> None:
    response = client.get("/no-existe")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert "request_id" in body["error"]


def test_cuerpo_demasiado_grande_devuelve_413(client: TestClient) -> None:
    max_bytes = get_settings().max_body_bytes
    big_payload = "x" * (max_bytes + 1)

    response = client.post("/healthz", content=big_payload)

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"


def test_cabeceras_de_seguridad_presentes(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "X-Request-Id" in response.headers


def test_error_de_validacion_devuelve_422_con_formato_unico() -> None:
    probe_app = FastAPI()
    register_error_handlers(probe_app)

    @probe_app.get("/probe")
    async def probe(valor: int):  # parámetro requerido y tipado, para forzar 422
        return {"valor": valor}

    with TestClient(probe_app, raise_server_exceptions=False) as probe_client:
        response = probe_client.get("/probe", params={"valor": "no-es-un-numero"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert "valor" in body["error"]["message"]
