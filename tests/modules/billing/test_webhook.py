from fastapi.testclient import TestClient

from tests.modules.billing.conftest import fake_signature_headers, fake_webhook_body


def _checkout_and_approve(client: TestClient, headers: dict, plan: str, amount: int = 19990) -> str:
    checkout = client.post("/billing/checkout", json={"plan": plan}, headers=headers)
    reference = checkout.json()["reference"]
    client.post(f"/billing/_dev/fake-approve/{reference}", json={"amount": amount})
    return reference


def test_pago_aprobado_activa_el_plan(client: TestClient, producer_headers: dict) -> None:
    reference = _checkout_and_approve(client, producer_headers, "pro")

    response = client.post(
        "/billing/webhooks/fake",
        content=fake_webhook_body(reference),
        headers=fake_signature_headers(),
    )

    assert response.status_code == 200
    subscripcion = client.get("/billing/subscription", headers=producer_headers).json()
    assert subscripcion["plan"] == "pro"
    assert subscripcion["plan_valid_until"] is not None


def test_aviso_con_firma_falsa_devuelve_401(client: TestClient, producer_headers: dict) -> None:
    reference = _checkout_and_approve(client, producer_headers, "pro")

    response = client.post(
        "/billing/webhooks/fake",
        content=fake_webhook_body(reference),
        headers={"x-fake-signature": "esto-no-es-el-secreto"},
    )

    assert response.status_code == 401
    perfil = client.get("/auth/me", headers=producer_headers).json()
    assert perfil["plan"] == "free"


def test_aviso_repetido_no_extiende_la_vigencia(client: TestClient, producer_headers: dict) -> None:
    reference = _checkout_and_approve(client, producer_headers, "pro")

    primero = client.post(
        "/billing/webhooks/fake", content=fake_webhook_body(reference), headers=fake_signature_headers()
    )
    vigencia_1 = client.get("/billing/subscription", headers=producer_headers).json()["plan_valid_until"]

    segundo = client.post(
        "/billing/webhooks/fake", content=fake_webhook_body(reference), headers=fake_signature_headers()
    )
    vigencia_2 = client.get("/billing/subscription", headers=producer_headers).json()["plan_valid_until"]

    assert primero.status_code == 200
    assert segundo.status_code == 200
    assert vigencia_1 == vigencia_2


def test_monto_distinto_al_esperado_no_activa_el_plan(
    client: TestClient, producer_headers: dict
) -> None:
    reference = _checkout_and_approve(client, producer_headers, "pro", amount=100)  # menor al plan

    response = client.post(
        "/billing/webhooks/fake",
        content=fake_webhook_body(reference),
        headers=fake_signature_headers(),
    )

    assert response.status_code == 200
    perfil = client.get("/auth/me", headers=producer_headers).json()
    assert perfil["plan"] == "free"


def test_pago_rechazado_no_cambia_el_plan(client: TestClient, producer_headers: dict) -> None:
    checkout = client.post("/billing/checkout", json={"plan": "pro"}, headers=producer_headers)
    reference = checkout.json()["reference"]
    client.post(f"/billing/_dev/fake-approve/{reference}", json={"status": "rejected"})

    response = client.post(
        "/billing/webhooks/fake",
        content=fake_webhook_body(reference),
        headers=fake_signature_headers(),
    )

    assert response.status_code == 200
    perfil = client.get("/auth/me", headers=producer_headers).json()
    assert perfil["plan"] == "free"
