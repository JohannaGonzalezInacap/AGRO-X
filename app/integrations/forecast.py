import httpx

from app.core.cache import TTLCache
from app.core.config import get_settings
from app.integrations.common import fetch_json, round_coordinate

MAX_FORECAST_DAYS = 16  # tope documentado por Open-Meteo (ADR-005).

_cache = TTLCache()


def _cache_key(latitude: float, longitude: float, days: int) -> str:
    return f"forecast:{latitude}:{longitude}:{days}"


def get_daily_forecast(
    latitude: float,
    longitude: float,
    days: int = 7,
    http_client: httpx.Client | None = None,
) -> dict[str, dict[str, float | None]]:
    """Pronóstico diario de Open-Meteo (ADR-005): máxima, mínima (°C) y lluvia (mm) por día.

    Open-Meteo no documenta un valor de relleno propio (a diferencia de NASA POWER, ADR-009): un
    dato ausente llega como `null` en el JSON y aquí queda igual, como `None`.
    """
    days = min(days, MAX_FORECAST_DAYS)
    rounded_lat = round_coordinate(latitude)
    rounded_lon = round_coordinate(longitude)
    key = _cache_key(rounded_lat, rounded_lon, days)

    cached = _cache.get(key)
    if cached is not None:
        return cached

    settings = get_settings()
    url = f"{settings.forecast_base_url}/v1/forecast"
    params = {
        "latitude": rounded_lat,
        "longitude": rounded_lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "forecast_days": days,
    }

    owns_client = http_client is None
    client = http_client or httpx.Client()
    try:
        payload = fetch_json(client, url, params, "La fuente de pronóstico")
    finally:
        if owns_client:
            client.close()

    daily = payload.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    precipitation = daily.get("precipitation_sum", [])

    result = {
        iso_date: {
            "t2m_max": max_temps[i] if i < len(max_temps) else None,
            "t2m_min": min_temps[i] if i < len(min_temps) else None,
            "precipitation_mm": precipitation[i] if i < len(precipitation) else None,
        }
        for i, iso_date in enumerate(dates)
    }

    _cache.set(key, result, get_settings().external_api_cache_ttl_seconds)
    return result
