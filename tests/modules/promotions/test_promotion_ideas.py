from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.auth.models import User
from tests.modules.promotions.conftest import (
    trigger_high_severity_alert,
    trigger_medium_severity_alert,
)


def test_plan_basico_recibe_ideas_si_hay_alerta_alta(
    client: TestClient, producer_with_farm, set_plan, monkeypatch
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    set_plan("promociones@example.com", "basic")
    trigger_high_severity_alert(client, farm_id, headers, monkeypatch)

    response = client.get(f"/farms/{farm_id}/promotions/ideas", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["alert_type"] == "frost"
    assert body[0]["ideas"]
    assert body[0]["illustrative"] is True


def test_sin_alerta_alta_no_hay_ideas(
    client: TestClient, producer_with_farm, set_plan, monkeypatch
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    set_plan("promociones@example.com", "pro")
    trigger_medium_severity_alert(client, farm_id, headers, monkeypatch)

    response = client.get(f"/farms/{farm_id}/promotions/ideas", headers=headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_plan_free_no_accede_a_las_ideas(
    client: TestClient, producer_with_farm, monkeypatch
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    trigger_high_severity_alert(client, farm_id, headers, monkeypatch)

    response = client.get(f"/farms/{farm_id}/promotions/ideas", headers=headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "plan_required"


def test_plan_vencido_se_comporta_como_free(
    client: TestClient, producer_with_farm, set_plan, monkeypatch, db_session
) -> None:
    headers = producer_with_farm["headers"]
    farm_id = producer_with_farm["farm_id"]
    set_plan("promociones@example.com", "pro")
    trigger_high_severity_alert(client, farm_id, headers, monkeypatch)

    user = db_session.scalar(select(User).where(User.email == "promociones@example.com"))
    user.plan_valid_until = datetime.now(UTC) - timedelta(days=1)
    db_session.commit()

    response = client.get(f"/farms/{farm_id}/promotions/ideas", headers=headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "plan_required"
