import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.auth.models import User
from tests.modules.farms.conftest import register_and_login


@pytest.fixture
def set_plan(db_session):
    def _set_plan(email: str, plan: str) -> None:
        user = db_session.scalar(select(User).where(User.email == email))
        user.plan = plan
        db_session.commit()

    return _set_plan


@pytest.fixture
def producer_pro_headers(client: TestClient, set_plan) -> dict:
    headers = register_and_login(client, "productor-pro@example.com", role="producer")
    set_plan("productor-pro@example.com", "pro")
    return headers


@pytest.fixture
def producer_free_headers(client: TestClient) -> dict:
    return register_and_login(client, "productor-free@example.com", role="producer")


@pytest.fixture
def merchant_pro_headers(client: TestClient, set_plan) -> dict:
    headers = register_and_login(client, "comerciante-pro@example.com", role="merchant")
    set_plan("comerciante-pro@example.com", "pro")
    return headers


@pytest.fixture
def merchant_free_headers(client: TestClient) -> dict:
    return register_and_login(client, "comerciante-free@example.com", role="merchant")
