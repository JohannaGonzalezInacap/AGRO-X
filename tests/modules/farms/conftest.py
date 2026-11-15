import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.auth.models import User

FARM_PAYLOAD = {
    "name": "Parcela Uno",
    "region": "Metropolitana",
    "latitude": -33.45,
    "longitude": -70.65,
    "area_hectares": 2.5,
}


def register_and_login(client: TestClient, email: str, role: str = "producer") -> dict:
    client.post(
        "/auth/register",
        json={"email": email, "name": "Alguien", "password": "clave-larga-123", "role": role},
    )
    login = client.post("/auth/login", json={"email": email, "password": "clave-larga-123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def producer_headers(client: TestClient) -> dict:
    return register_and_login(client, "productora@example.com", role="producer")


@pytest.fixture
def set_plan(db_session):
    def _set_plan(email: str, plan: str) -> None:
        user = db_session.scalar(select(User).where(User.email == email))
        user.plan = plan
        db_session.commit()

    return _set_plan
