from datetime import date

import httpx

from app.core.cache import TTLCache
from app.core.config import get_settings
from app.integrations.common import as_observed_value, fetch_json, round_coordinate

PARAMETERS = ["T2M_MAX", "T2M_MIN", "PRECTOTCORR", "GWETROOT"]

_cache = TTLCache()


def _cache_key(latitude: float, longitude: float, start: date, end: date) -> str:
    return f"nasa_power:{latitude}:{longitude}:{start.isoformat()}:{end.isoformat()}"


def get_daily_observations(
    latitude: float,
    longitude: float,
    start: date,
    end: date,
    http_client: httpx.Client | None = None,
) -> dict[str, dict[str, float | None]]:
    """Observaciones diarias de NASA POWER (ADR-005): temperatura máxima y mínima (°C),
    precipitación corregida (mm/día) y humedad del suelo en zona de raíces (0 a 1).

    Devuelve un dict por fecha ISO (YYYY-MM-DD); un día sin dato queda con valores `None`
    (spec/contratos/fuentes-datos.md). Usa caché: no repite la misma consulta dos veces seguidas.
    """
    rounded_lat = round_coordinate(latitude)
    rounded_lon = round_coordinate(longitude)
    key = _cache_key(rounded_lat, rounded_lon, start, end)

    cached = _cache.get(key)
    if cached is not None:
        return cached

    settings = get_settings()
    url = f"{settings.nasa_power_base_url}/api/temporal/daily/point"
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "AG",
        "latitude": rounded_lat,
        "longitude": rounded_lon,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }

    owns_client = http_client is None
    client = http_client or httpx.Client()
    try:
        payload = fetch_json(client, url, params, "NASA POWER")
    finally:
        if owns_client:
            client.close()

    parameter_data = payload.get("properties", {}).get("parameter", {})
    result: dict[str, dict[str, float | None]] = {}
    all_dates = set()
    for series in parameter_data.values():
        all_dates.update(series.keys())

    for raw_date in sorted(all_dates):
        iso_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
        result[iso_date] = {
            "t2m_max": as_observed_value(parameter_data.get("T2M_MAX", {}).get(raw_date)),
            "t2m_min": as_observed_value(parameter_data.get("T2M_MIN", {}).get(raw_date)),
            "precipitation_mm": as_observed_value(
                parameter_data.get("PRECTOTCORR", {}).get(raw_date)
            ),
            "soil_moisture": as_observed_value(parameter_data.get("GWETROOT", {}).get(raw_date)),
        }

    _cache.set(key, result, get_settings().external_api_cache_ttl_seconds)
    return result
