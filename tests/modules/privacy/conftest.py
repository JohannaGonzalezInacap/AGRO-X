import pytest
from fastapi.testclient import TestClient

from tests.modules.farms.conftest import FARM_PAYLOAD, register_and_login


@pytest.fixture
def producer_with_farm(client: TestClient) -> dict:
    headers = register_and_login(client, "privacidad@example.com", role="producer")
    farm = client.post("/farms", json=FARM_PAYLOAD, headers=headers)
    return {"headers": headers, "farm_id": farm.json()["id"]}
