import json

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.modules.billing.providers import fake as fake_provider
from tests.modules.farms.conftest import register_and_login


@pytest.fixture(autouse=True)
def _clear_fake_results():
    fake_provider.clear_simulated_results()
    yield
    fake_provider.clear_simulated_results()


@pytest.fixture
def producer_headers(client: TestClient) -> dict:
    return register_and_login(client, "pagos@example.com", role="producer")


def fake_webhook_body(reference: str, event_id: str | None = None) -> bytes:
    return json.dumps({"reference": reference, "event_id": event_id or reference}).encode("utf-8")


def fake_signature_headers() -> dict:
    return {"x-fake-signature": get_settings().payment_webhook_secret}
