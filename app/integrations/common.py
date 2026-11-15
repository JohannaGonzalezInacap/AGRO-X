import httpx

from app.core.config import get_settings
from app.core.errors import AppError

# NASA POWER usa -999 como valor de relleno ("sin dato"); el margen hasta -990 cubre variantes
# como -999.0 o -9999 sin tener que listarlas todas (ver ADR-009).
_MISSING_VALUE_THRESHOLD = -990.0


def round_coordinate(value: float) -> float:
    """Redondea una coordenada antes de enviarla a cualquier fuente externa (ADR-009)."""
    return round(value, get_settings().coordinate_rounding_decimals)


def as_observed_value(raw: float | None) -> float | None:
    """Un valor de relleno (sin dato) se trata como `None`, nunca como número."""
    if raw is None or raw <= _MISSING_VALUE_THRESHOLD:
        return None
    return raw


def fetch_json(
    client: httpx.Client, url: str, params: dict, provider_label: str
) -> dict:
    """GET con el tiempo de espera configurado; cualquier falla se convierte en 502
    `upstream_unavailable` (spec/contratos/fuentes-datos.md, regla 2)."""
    try:
        response = client.get(url, params=params, timeout=get_settings().external_api_timeout_seconds)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AppError(
            502, "upstream_unavailable", f"{provider_label} no respondió. Intenta más tarde."
        ) from exc
    return response.json()
