import httpx
import pytest

from app.core.errors import AppError
from app.integrations import forecast

FAKE_RESPONSE = {
    "daily": {
        "time": ["2026-11-15", "2026-11-16"],
        "temperature_2m_max": [22.1, 24.0],
        "temperature_2m_min": [8.3, None],
        "precipitation_sum": [0.0, 1.2],
    }
}


def _client_with_response(json_body: dict, status_code: int = 200) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_dia_con_dato_llega_con_sus_valores() -> None:
    client = _client_with_response(FAKE_RESPONSE)

    result = forecast.get_daily_forecast(-33.45, -70.65, days=2, http_client=client)

    assert result["2026-11-15"]["t2m_max"] == 22.1
    assert result["2026-11-15"]["precipitation_mm"] == 0.0


def test_dato_ausente_llega_como_none() -> None:
    client = _client_with_response(FAKE_RESPONSE)

    result = forecast.get_daily_forecast(-33.45, -70.65, days=2, http_client=client)

    assert result["2026-11-16"]["t2m_min"] is None


def test_falla_la_fuente_externa_devuelve_502() -> None:
    client = _client_with_response({}, status_code=503)

    with pytest.raises(AppError) as exc_info:
        forecast.get_daily_forecast(-33.45, -70.65, days=2, http_client=client)

    assert exc_info.value.status_code == 502
    assert exc_info.value.code == "upstream_unavailable"


def test_la_cache_evita_una_segunda_llamada() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(200, json=FAKE_RESPONSE)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    forecast.get_daily_forecast(-33.45, -70.65, days=2, http_client=client)
    forecast.get_daily_forecast(-33.45, -70.65, days=2, http_client=client)

    assert calls["count"] == 1


def test_el_tope_de_dias_es_16() -> None:
    received_params = {}

    def handler(request: httpx.Request) -> httpx.Response:
        received_params.update(request.url.params)
        return httpx.Response(200, json=FAKE_RESPONSE)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    forecast.get_daily_forecast(-33.45, -70.65, days=30, http_client=client)

    assert received_params["forecast_days"] == "16"
