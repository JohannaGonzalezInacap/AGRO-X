import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import plans
from app.core.errors import AppError
from app.core.time import as_aware_utc
from app.integrations import forecast, nasa_power
from app.modules.alerts.models import Alert
from app.modules.alerts.schemas import AlertResponse
from app.modules.auth.models import User
from app.modules.farms.models import CropHistory
from app.modules.farms.service import get_owned_farm_or_404
from app.modules.rotation.models import Crop
from app.modules.rotation.schemas import RecommendationRequest
from app.modules.rotation.service import recommend_rotation

# ADR-011: umbrales ilustrativos (salvo el de 0 °C, convención meteorológica real de helada).
_FROST_THRESHOLDS_C = {"baja": 2.0, "media": 0.0, "alta": -2.0}
_HEAT_THRESHOLDS_C = {"baja": 30.0, "media": 33.0, "alta": 36.0}
_DROUGHT_SOIL_MOISTURE_THRESHOLD = 0.25
_DROUGHT_RAIN_THRESHOLD_MM_7D = 5.0
_HEAVY_RAIN_THRESHOLD_MM = 25.0
_FORECAST_WINDOW_DAYS = 7
_OBSERVATION_WINDOW_DAYS = 7

_DEFAULT_TOLERANCE = "media"
_HARVEST_STAGE = "cosecha"


def _recent_crop_history(db: Session, farm_id: uuid.UUID) -> list[CropHistory]:
    return list(
        db.scalars(
            select(CropHistory)
            .where(CropHistory.farm_id == farm_id)
            .order_by(CropHistory.created_at.desc())
        )
    )


def _evaluate_frost(forecast_data: dict, tolerance: str) -> dict | None:
    threshold = _FROST_THRESHOLDS_C.get(tolerance, _FROST_THRESHOLDS_C[_DEFAULT_TOLERANCE])
    for day, values in sorted(forecast_data.items()):
        t_min = values.get("t2m_min")
        if t_min is None or t_min > threshold:
            continue
        severity = "alta" if t_min <= threshold - 3 else "media"
        return {
            "type": "frost",
            "severity": severity,
            "title": "Riesgo de helada",
            "expected_date": date.fromisoformat(day),
            "detail": f"Se pronostica una mínima de {t_min} °C el {day}, bajo el umbral de"
            f" {threshold} °C para este cultivo (ADR-011).",
            "recommendations": "Considera riego por aspersión o cobertura la noche anterior.",
            "illustrative": True,
            "sources_used": "pronostico",
        }
    return None


def _evaluate_heat(forecast_data: dict, tolerance: str) -> dict | None:
    threshold = _HEAT_THRESHOLDS_C.get(tolerance, _HEAT_THRESHOLDS_C[_DEFAULT_TOLERANCE])
    for day, values in sorted(forecast_data.items()):
        t_max = values.get("t2m_max")
        if t_max is None or t_max < threshold:
            continue
        severity = "alta" if t_max >= threshold + 3 else "media"
        return {
            "type": "extreme_heat",
            "severity": severity,
            "title": "Riesgo de calor extremo",
            "expected_date": date.fromisoformat(day),
            "detail": f"Se pronostica una máxima de {t_max} °C el {day}, sobre el umbral de"
            f" {threshold} °C para este cultivo (ADR-011).",
            "recommendations": "Evalúa riego adicional y sombra si el cultivo lo permite.",
            "illustrative": True,
            "sources_used": "pronostico",
        }
    return None


def _evaluate_drought(observations: dict, forecast_data: dict) -> dict | None:
    soil_moisture_values = [
        v["soil_moisture"] for v in observations.values() if v.get("soil_moisture") is not None
    ]
    if not soil_moisture_values:
        return None  # sin dato suficiente, no se afirma sequía (ADR-011).

    average_moisture = sum(soil_moisture_values) / len(soil_moisture_values)
    total_forecast_rain = sum(
        v["precipitation_mm"] for v in forecast_data.values() if v.get("precipitation_mm") is not None
    )
    if (
        average_moisture >= _DROUGHT_SOIL_MOISTURE_THRESHOLD
        or total_forecast_rain >= _DROUGHT_RAIN_THRESHOLD_MM_7D
    ):
        return None

    return {
        "type": "drought",
        "severity": "media",
        "title": "Riesgo de sequía",
        "expected_date": None,
        "detail": f"Humedad de suelo promedio {average_moisture:.2f} (bajo"
        f" {_DROUGHT_SOIL_MOISTURE_THRESHOLD}) y solo {total_forecast_rain:.1f} mm de lluvia"
        f" pronosticada en los próximos {_FORECAST_WINDOW_DAYS} días (ADR-011).",
        "recommendations": "Prioriza el riego disponible en los cultivos de mayor valor.",
        "illustrative": True,
        "sources_used": "nasa_power,pronostico",
    }


def _evaluate_heavy_rain(forecast_data: dict) -> dict | None:
    for day, values in sorted(forecast_data.items()):
        rain = values.get("precipitation_mm")
        if rain is None or rain < _HEAVY_RAIN_THRESHOLD_MM:
            continue
        return {
            "type": "heavy_rain",
            "severity": "alta" if rain >= _HEAVY_RAIN_THRESHOLD_MM * 1.5 else "media",
            "title": "Riesgo de lluvia intensa",
            "expected_date": date.fromisoformat(day),
            "detail": f"Se pronostican {rain} mm el {day}, sobre el umbral de"
            f" {_HEAVY_RAIN_THRESHOLD_MM} mm (ADR-011).",
            "recommendations": "Revisa drenaje de la parcela antes de la fecha esperada.",
            "illustrative": True,
            "sources_used": "pronostico",
        }
    return None


def _build_crop_change_alert(db: Session, owner: User, farm_id: uuid.UUID) -> dict:
    sources = ["historial_de_parcela"]
    suggestion_crop = None
    suggestion_reasons: list[str] = []

    if plans.crop_suggestion_allowed(owner):
        try:
            recommendation = recommend_rotation(db, owner, farm_id, RecommendationRequest())
            # Este aviso es para cambiar de cultivo (regla 13, dominio.md): nunca sugiere quedarse
            # con el mismo, aunque esa opción haya puntuado más alto en la comparación general.
            top = next((item for item in recommendation.items if not item.is_current), None)
            if top is not None:
                suggestion_crop = top.crop
                suggestion_reasons = top.reasons
                sources.append("motor_de_rotacion")
        except AppError:
            suggestion_crop = None  # sin datos suficientes para recomendar (rotacion.feature).

    if suggestion_crop:
        detail = f"Conviene plantar '{suggestion_crop}' la siguiente temporada."
        recommendations = " ".join(suggestion_reasons)
    else:
        detail = "Conviene cambiar el cultivo de esta parcela la siguiente temporada."
        recommendations = None

    return {
        "type": "crop_change",
        "severity": "media",
        "title": "Es hora de cambiar el cultivo",
        "expected_date": None,
        "detail": detail,
        "recommendations": recommendations,
        "suggested_crop": suggestion_crop,
        "illustrative": True,
        "sources_used": ",".join(sources),
    }


def _sync_alerts(db: Session, farm_id: uuid.UUID, computed: list[dict]) -> None:
    db.query(Alert).filter(Alert.farm_id == farm_id, Alert.active.is_(True)).update(
        {"active": False}
    )
    for data in computed:
        db.add(Alert(farm_id=farm_id, active=True, **data))


def refresh_alerts(db: Session, owner: User, farm_id: uuid.UUID) -> list[Alert]:
    farm = get_owned_farm_or_404(db, owner, farm_id)

    interval = plans.alert_refresh_interval_for(owner)
    if farm.alerts_refreshed_at is not None:
        next_allowed = as_aware_utc(farm.alerts_refreshed_at) + interval
        if datetime.now(UTC) < next_allowed:
            raise AppError(
                429,
                "too_soon",
                f"Ya recalculaste alertas recientemente. Podrás hacerlo de nuevo el"
                f" {next_allowed.date().isoformat()}.",
            )

    # Si cualquiera de estas dos llamadas falla, AppError(502) se propaga aquí y no se toca nada
    # de lo ya guardado (spec/bdd/alertas.feature: "las alertas anteriores siguen disponibles").
    forecast_data = forecast.get_daily_forecast(farm.latitude, farm.longitude, days=_FORECAST_WINDOW_DAYS)
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=_OBSERVATION_WINDOW_DAYS - 1)
    observations = nasa_power.get_daily_observations(farm.latitude, farm.longitude, start, end)

    history = _recent_crop_history(db, farm_id)
    current_entry = history[0] if history else None
    current_crop = (
        db.scalar(select(Crop).where(Crop.name == current_entry.crop)) if current_entry else None
    )
    frost_tolerance = current_crop.frost_tolerance if current_crop else _DEFAULT_TOLERANCE
    heat_tolerance = current_crop.heat_tolerance if current_crop else _DEFAULT_TOLERANCE

    computed = []
    for alert_data in (
        _evaluate_frost(forecast_data, frost_tolerance),
        _evaluate_heat(forecast_data, heat_tolerance),
        _evaluate_drought(observations, forecast_data),
        _evaluate_heavy_rain(forecast_data),
    ):
        if alert_data is not None:
            computed.append(alert_data)

    if (
        current_entry is not None
        and current_entry.stage == _HARVEST_STAGE
        and plans.crop_change_alert_allowed(owner)
    ):
        computed.append(_build_crop_change_alert(db, owner, farm_id))

    _sync_alerts(db, farm_id, computed)
    farm.alerts_refreshed_at = datetime.now(UTC)
    db.commit()

    return _active_alerts(db, farm_id)


def _active_alerts(db: Session, farm_id: uuid.UUID) -> list[Alert]:
    return list(
        db.scalars(
            select(Alert)
            .where(Alert.farm_id == farm_id, Alert.active.is_(True))
            .order_by(Alert.created_at.desc())
        )
    )


def list_alerts(db: Session, owner: User, farm_id: uuid.UUID) -> list[Alert]:
    get_owned_farm_or_404(db, owner, farm_id)
    return _active_alerts(db, farm_id)


def to_response(alert: Alert, owner: User) -> AlertResponse:
    show_detail = plans.alert_detail_allowed(owner)
    return AlertResponse(
        id=alert.id,
        type=alert.type,
        severity=alert.severity,
        title=alert.title,
        expected_date=alert.expected_date,
        detail=alert.detail if show_detail else None,
        recommendations=alert.recommendations if show_detail else None,
        suggested_crop=alert.suggested_crop if show_detail else None,
        illustrative=alert.illustrative,
        sources_used=[s for s in alert.sources_used.split(",") if s],
        created_at=alert.created_at,
    )
