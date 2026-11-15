from datetime import date

import httpx
import pytest

from app.core.errors import AppError
from app.integrations import nasa_power

FAKE_RESPONSE = {
    "properties": {
        "parameter": {
            "T2M_MAX": {"20261101": 19.14, "20261102": -999},
            "T2M_MIN": {"20261101": 6.45, "20261102": -999},
            "PRECTOTCORR": {"20261101": 0.12, "20261102": 0.0},
            "GWETROOT": {"20261101": 0.35, "20261102": 0.33},
        }
    }
}


def _client_with_response(json_body: dict, status_code: int = 200) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_dia_con_dato_llega_con_sus_valores() -> None:
    client = _client_with_response(FAKE_RESPONSE)

    result = nasa_power.get_daily_observations(
        -33.45, -70.65, date(2026, 11, 1), date(2026, 11, 2), http_client=client
    )

    assert result["2026-11-01"]["t2m_max"] == 19.14
    assert result["2026-11-01"]["soil_moisture"] == 0.35


def test_valor_de_relleno_se_trata_como_sin_dato() -> None:
    client = _client_with_response(FAKE_RESPONSE)

    result = nasa_power.get_daily_observations(
        -33.45, -70.65, date(2026, 11, 1), date(2026, 11, 2), http_client=client
    )

    assert result["2026-11-02"]["t2m_max"] is None
    assert result["2026-11-02"]["t2m_min"] is None
    # PRECTOTCORR sí trajo dato (0.0 no es relleno, es "no llovió").
    assert result["2026-11-02"]["precipitation_mm"] == 0.0


def test_falla_la_fuente_externa_devuelve_502() -> None:
    client = _client_with_response({}, status_code=503)

    with pytest.raises(AppError) as exc_info:
        nasa_power.get_daily_observations(
            -33.45, -70.65, date(2026, 11, 1), date(2026, 11, 2), http_client=client
        )

    assert exc_info.value.status_code == 502
    assert exc_info.value.code == "upstream_unavailable"


def test_la_cache_evita_una_segunda_llamada() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(200, json=FAKE_RESPONSE)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    nasa_power.get_daily_observations(
        -33.45, -70.65, date(2026, 11, 1), date(2026, 11, 2), http_client=client
    )
    nasa_power.get_daily_observations(
        -33.45, -70.65, date(2026, 11, 1), date(2026, 11, 2), http_client=client
    )

    assert calls["count"] == 1


def test_redondea_las_coordenadas_antes_de_llamar() -> None:
    received_params = {}

    def handler(request: httpx.Request) -> httpx.Response:
        received_params.update(request.url.params)
        return httpx.Response(200, json=FAKE_RESPONSE)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    nasa_power.get_daily_observations(
        -33.456789, -70.654321, date(2026, 11, 1), date(2026, 11, 2), http_client=client
    )

    assert received_params["latitude"] == "-33.46"
    assert received_params["longitude"] == "-70.65"
