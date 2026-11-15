from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.auth.models import User
from tests.modules.farms.conftest import FARM_PAYLOAD


def test_plan_free_tope_de_una_parcela(client: TestClient, producer_headers: dict) -> None:
    primera = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
    assert primera.status_code == 201

    segunda = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)

    assert segunda.status_code == 403
    assert segunda.json()["error"]["code"] == "plan_required"


def test_plan_basico_tope_de_tres_parcelas(
    client: TestClient, producer_headers: dict, set_plan
) -> None:
    set_plan("productora@example.com", "basic")

    for _ in range(3):
        response = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
        assert response.status_code == 201

    cuarta = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
    assert cuarta.status_code == 403


def test_plan_vencido_se_comporta_como_free(
    client: TestClient, producer_headers: dict, db_session
) -> None:
    user = db_session.scalar(select(User).where(User.email == "productora@example.com"))
    user.plan = "pro"
    user.plan_valid_until = datetime.now(UTC) - timedelta(days=1)
    db_session.commit()

    primera = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
    assert primera.status_code == 201

    segunda = client.post("/farms", json=FARM_PAYLOAD, headers=producer_headers)
    assert segunda.status_code == 403
