import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.integrations import nasa_power
from app.modules.auth.models import User
from app.modules.farms.models import CropHistory, Farm
from app.modules.farms.service import get_owned_farm_or_404
from app.modules.rotation.models import Crop
from app.modules.rotation.schemas import (
    CropResponse,
    PriorityDimension,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
)

# ADR-010: ventana y umbral para "baja precipitación".
_PRECIPITATION_WINDOW_DAYS = 14
_LOW_PRECIPITATION_THRESHOLD_MM = 2.0

_FAMILY_REPEAT_PENALTY = 25
_NITROGEN_FIX_BONUS = 30
_HIGH_WATER_NEED_PENALTY = 20


def list_crops(db: Session) -> list[CropResponse]:
    crops = db.scalars(select(Crop).order_by(Crop.name)).all()
    return [_to_crop_response(c) for c in crops]


def _to_crop_response(crop: Crop) -> CropResponse:
    return CropResponse(
        id=crop.id,
        name=crop.name,
        family=crop.family,
        water_need=crop.water_need,
        nitrogen_effect=crop.nitrogen_effect,
        root_depth=crop.root_depth,
        frost_tolerance=crop.frost_tolerance,
        heat_tolerance=crop.heat_tolerance,
        illustrative=crop.source is None,
    )


def _recent_crop_history(db: Session, farm_id: uuid.UUID) -> list[CropHistory]:
    return list(
        db.scalars(
            select(CropHistory)
            .where(CropHistory.farm_id == farm_id)
            .order_by(CropHistory.created_at.desc())
        )
    )


def _average_recent_precipitation(latitude: float, longitude: float) -> float | None:
    """Promedio de mm/día en los últimos 14 días (ADR-010). `None` si ningún día tuvo dato."""
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=_PRECIPITATION_WINDOW_DAYS - 1)
    observations = nasa_power.get_daily_observations(latitude, longitude, start, end)
    values = [day["precipitation_mm"] for day in observations.values() if day["precipitation_mm"] is not None]
    if not values:
        return None
    return sum(values) / len(values)


def recommend_rotation(
    db: Session, owner: User, farm_id: uuid.UUID, request: RecommendationRequest
) -> RecommendationResponse:
    farm = get_owned_farm_or_404(db, owner, farm_id)
    history = _recent_crop_history(db, farm_id)
    all_crops = db.scalars(select(Crop)).all()
    crops_by_name = {c.name: c for c in all_crops}

    notices: list[str] = []
    sources_used = ["catalogo_cultivos"]

    current_crop_name = history[0].crop if history else None
    current_crop = crops_by_name.get(current_crop_name) if current_crop_name else None

    if history:
        sources_used.append("historial_de_parcela")
    else:
        notices.append(
            "Sin historial de cultivos: la recomendación se basa solo en clima y suelo."
        )

    last_two_families = {
        crops_by_name[h.crop].family for h in history[:2] if h.crop in crops_by_name
    }
    # Para evaluar "quedarse" con el cultivo vigente, se mira la familia de las temporadas
    # ANTERIORES a él (no la suya propia, que siempre "coincidiría consigo misma" y no diría nada).
    families_before_current = {
        crops_by_name[h.crop].family for h in history[1:3] if h.crop in crops_by_name
    }

    average_precipitation = None
    try:
        average_precipitation = _average_recent_precipitation(farm.latitude, farm.longitude)
        sources_used.append("nasa_power")
    except AppError:
        notices.append("No se pudo consultar el clima; la recomendación no usa ese dato.")

    low_precipitation = average_precipitation is not None and (
        average_precipitation < _LOW_PRECIPITATION_THRESHOLD_MM
    )
    if average_precipitation is None and "nasa_power" in sources_used:
        notices.append(
            "Los últimos 14 días no tienen dato de precipitación; no se pudo evaluar si la zona"
            " está seca."
        )

    top_priority = request.priorities[0] if request.priorities else PriorityDimension.WATER
    if PriorityDimension.SOIL in request.priorities:
        notices.append(
            "La prioridad de suelo todavía no afecta el puntaje: falta definir la regla de"
            " negocio (ver plan de la Fase 5)."
        )
    if PriorityDimension.INCOME in request.priorities:
        notices.append(
            "La prioridad de ingreso todavía no afecta el puntaje: no hay fuente de precios de"
            " mercado (spec/contratos/fuentes-datos.md)."
        )

    items: list[RecommendationItem] = []
    for crop in all_crops:
        if crop.name == current_crop_name:
            continue  # se compara aparte, como "quedarse" (ver current_item más abajo).

        score = 100
        reasons: list[str] = []

        if current_crop is not None and current_crop.nitrogen_effect == "consume" and crop.nitrogen_effect == "fija":
            score += _NITROGEN_FIX_BONUS
            reasons.append("Repone nitrógeno después de un cultivo exigente.")

        if crop.family in last_two_families:
            score -= _FAMILY_REPEAT_PENALTY
            reasons.append("Repetir la familia favorece plagas y enfermedades.")

        if (
            not farm.has_irrigation
            and low_precipitation
            and top_priority == PriorityDimension.WATER
            and crop.water_need == "alto"
        ):
            score -= _HIGH_WATER_NEED_PENALTY
            reasons.append("Alta demanda de agua, no conviene con poca disponibilidad (ADR-010).")

        if not reasons:
            reasons.append(
                f"Cultivo de la familia {crop.family}, sin un motivo específico para subir o"
                " bajar su puntaje esta temporada."
            )

        items.append(
            RecommendationItem(
                crop=crop.name,
                score=score,
                reasons=reasons,
                illustrative=crop.source is None,
            )
        )

    if current_crop is not None:
        items.append(
            _current_strategy_item(
                current_crop, families_before_current, farm, low_precipitation, top_priority
            )
        )

    items.sort(key=lambda item: item.score, reverse=True)

    return RecommendationResponse(items=items, sources_used=sources_used, notices=notices)


def _current_strategy_item(
    current_crop: Crop,
    families_before_current: set[str],
    farm: Farm,
    low_precipitation: bool,
    top_priority: PriorityDimension,
) -> RecommendationItem:
    """La estrategia de "quedarse" con el cultivo vigente, comparada igual que las alternativas
    de rotación (el reto pide comparar "al menos tres estrategias... incluida la actual")."""
    score = 100
    reasons: list[str] = []

    if current_crop.family in families_before_current:
        score -= _FAMILY_REPEAT_PENALTY
        reasons.append(
            "Seguir con este cultivo repite otra vez la misma familia reciente, lo que favorece"
            " plagas y enfermedades."
        )

    if (
        not farm.has_irrigation
        and low_precipitation
        and top_priority == PriorityDimension.WATER
        and current_crop.water_need == "alto"
    ):
        score -= _HIGH_WATER_NEED_PENALTY
        reasons.append(
            "Alta demanda de agua; seguir con este cultivo no ayuda con la poca disponibilidad"
            " (ADR-010)."
        )

    if not reasons:
        reasons.append("Es el cultivo vigente de esta parcela: la opción de no rotar todavía.")

    return RecommendationItem(
        crop=current_crop.name,
        score=score,
        reasons=reasons,
        illustrative=current_crop.source is None,
        is_current=True,
    )
