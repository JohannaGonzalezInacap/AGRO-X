import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import plans
from app.core.errors import AppError
from app.modules.alerts.models import Alert
from app.modules.auth.models import User
from app.modules.farms.models import CropHistory
from app.modules.farms.service import get_owned_farm_or_404
from app.modules.promotions.schemas import PromotionIdeaResponse

_HIGH_SEVERITY = "alta"

# ADR-013: sugerencias ilustrativas por tipo de alerta. "{crop}" se rellena con el cultivo vigente
# de la parcela, o una frase genérica si no hay ninguno registrado.
_IDEAS_BY_ALERT_TYPE: dict[str, list[str]] = {
    "frost": [
        (
            "Adelanta la cosecha de {crop} que ya esté lista y ofrécela esta semana a vecinos,"
            " ferias o almacenes cercanos antes de que llegue la helada."
        ),
        (
            "Avisa por redes sociales o grupos de WhatsApp del sector que hay {crop} disponible"
            " con urgencia, a precio de salida rápida."
        ),
    ],
    "extreme_heat": [
        (
            "Cosecha y vende primero la parte de {crop} más expuesta al sol, antes de que el"
            " calor siga dañándola."
        ),
        (
            "Ofrece {crop} con descuento por volumen a restaurantes o almacenes que puedan"
            " llevárselo rápido, mientras aún está en buen estado."
        ),
    ],
    "drought": [
        "Prioriza vender ya la parte de {crop} que dependa más del riego que te está faltando.",
        (
            "Contacta directamente a compradores habituales de {crop} para una venta anticipada,"
            " antes de que la sequía reduzca más la calidad."
        ),
    ],
    "heavy_rain": [
        (
            "Si puedes cosechar antes de la lluvia intensa, hazlo y vende {crop} de inmediato"
            " para no perderla por exceso de agua."
        ),
        (
            "Avisa a compradores cercanos que hay {crop} disponible ahora, antes de que el acceso"
            " a la parcela se complique con la lluvia."
        ),
    ],
}

_GENERIC_IDEAS = [
    (
        "Vende {crop} lo antes posible a vecinos, ferias locales o almacenes cercanos, antes de"
        " que el riesgo señalado avance."
    ),
    "Avisa por redes sociales o contactos directos que hay {crop} disponible con urgencia.",
]


def _current_crop_name(db: Session, farm_id: uuid.UUID) -> str | None:
    entry = db.scalar(
        select(CropHistory).where(CropHistory.farm_id == farm_id, CropHistory.current.is_(True))
    )
    return entry.crop if entry else None


def _build_ideas(alert: Alert, crop: str | None) -> list[str]:
    crop_label = crop or "tu cosecha"
    templates = _IDEAS_BY_ALERT_TYPE.get(alert.type, _GENERIC_IDEAS)
    return [t.format(crop=crop_label) for t in templates]


def get_promotion_ideas(db: Session, owner: User, farm_id: uuid.UUID) -> list[PromotionIdeaResponse]:
    get_owned_farm_or_404(db, owner, farm_id)

    if not plans.promotion_ideas_allowed(owner):
        raise AppError(
            403, "plan_required", "Esta función requiere plan básico o pro."
        )

    high_severity_alerts = list(
        db.scalars(
            select(Alert)
            .where(
                Alert.farm_id == farm_id,
                Alert.active.is_(True),
                Alert.severity == _HIGH_SEVERITY,
            )
            .order_by(Alert.created_at.desc())
        )
    )
    if not high_severity_alerts:
        raise AppError(
            404,
            "not_found",
            "No hay alertas de riesgo alto activas; todavía no hay ideas de venta urgente para"
            " esta parcela.",
        )

    crop = _current_crop_name(db, farm_id)
    sources = ["alertas_activas"] + (["historial_de_parcela"] if crop else [])

    return [
        PromotionIdeaResponse(
            alert_id=alert.id,
            alert_type=alert.type,
            alert_title=alert.title,
            crop=crop,
            ideas=_build_ideas(alert, crop),
            illustrative=True,
            sources_used=sources,
        )
        for alert in high_severity_alerts
    ]
