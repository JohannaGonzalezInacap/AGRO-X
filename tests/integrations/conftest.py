import pytest

from app.integrations import forecast, nasa_power


@pytest.fixture(autouse=True)
def _clear_integration_caches():
    nasa_power._cache.clear()
    forecast._cache.clear()
    yield
    nasa_power._cache.clear()
    forecast._cache.clear()
