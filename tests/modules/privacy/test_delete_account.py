import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.alerts.models import Alert
from app.modules.billing.models import Payment
from app.modules.farms.models import CropHistory, Farm


def test_eliminar_mi_cuenta_borra_mis_datos_de_las_tablas_activas(
    client: TestClient, producer_with_farm, db_session
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = uuid.UUID(producer_with_farm["farm_id"])
    client.post(
        f"/farms/{farm_id}/crop-history",
        json={"crop": "maiz", "planting_date": "2026-01-10", "stage": "crecimiento"},
        headers=headers,
    )
    db_session.add(
        Alert(
            farm_id=farm_id,
            type="frost",
            severity="alta",
            title="Riesgo de helada",
            illustrative=True,
            sources_used="pronostico",
            active=True,
        )
    )
    db_session.commit()

    response = client.delete("/privacy/account", headers=headers)
    assert response.status_code == 204

    login = client.post(
        "/auth/login",
        json={"email": "privacidad@example.com", "password": "clave-larga-123"},
    )
    assert login.status_code == 401

    assert db_session.scalar(select(Farm).where(Farm.id == farm_id)) is None
    assert db_session.scalar(select(CropHistory).where(CropHistory.farm_id == farm_id)) is None
    assert db_session.scalar(select(Alert).where(Alert.farm_id == farm_id)) is None


def test_eliminar_mi_cuenta_anonimiza_mis_pagos_no_los_borra(
    client: TestClient, producer_with_farm, db_session
) -> None:
    headers = producer_with_farm["headers"]
    checkout = client.post("/billing/checkout", json={"plan": "basic"}, headers=headers)
    reference = uuid.UUID(checkout.json()["reference"])

    response = client.delete("/privacy/account", headers=headers)
    assert response.status_code == 204

    payment = db_session.scalar(select(Payment).where(Payment.reference == reference))
    assert payment is not None
    assert payment.user_id is None
