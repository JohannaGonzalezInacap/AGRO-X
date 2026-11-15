from datetime import UTC, datetime, timedelta

from app.core.time import as_aware_utc
from app.modules.auth.models import User

FREE = "free"
BASIC = "basic"
PRO = "pro"

# Fuente de verdad: spec/alcance-y-planes.md. Cambiar qué incluye un plan es cambiar esta tabla,
# no reescribir rutas (ADR-006). Por ahora solo el tope de parcelas (Fase 3); las Fases 6 y 7
# agregan aquí mismo la frecuencia de alertas y el control de rutas por plan.
MAX_FARMS_BY_PLAN = {
    FREE: 1,
    BASIC: 3,
    PRO: 20,
}

# Frecuencia de recálculo de alertas (Fase 6, spec/alcance-y-planes.md).
ALERT_REFRESH_INTERVAL = {
    FREE: timedelta(days=30),
    BASIC: timedelta(days=1),
    PRO: timedelta(hours=6),
}

# Contenido de la alerta (Fase 6, spec/alcance-y-planes.md): free solo ve el resumen; básico y
# pro ven detalle y recomendaciones ("Igual que básico").
PLANS_WITH_ALERT_DETAIL = {BASIC, PRO}

# Alerta de cambio de cultivo (ADR-008): free no la recibe; pro además ve la sugerencia de
# rotación.
PLANS_WITH_CROP_CHANGE_ALERT = {BASIC, PRO}
PLANS_WITH_CROP_SUGGESTION = {PRO}

# Mercado (Fase 8, spec/alcance-y-planes.md): listar comerciantes y publicar mermas, del lado del
# productor.
PLANS_WITH_MARKETPLACE_ACCESS = {PRO}

# ND-001 (spec/alcance-y-planes.md): el comerciante también paga plan para ver el contacto de una
# merma, aunque el productor la haya publicado con el contacto visible.
PLANS_WITH_MERCHANT_CONTACT_VISIBILITY = {PRO}


def effective_plan(user: User) -> str:
    """Un plan vencido se comporta como free, sin borrar nada (dominio.md regla 3)."""
    if user.plan == FREE:
        return FREE
    if user.plan_valid_until is None:
        return user.plan
    if as_aware_utc(user.plan_valid_until) < datetime.now(UTC):
        return FREE
    return user.plan


def max_farms_for(user: User) -> int:
    return MAX_FARMS_BY_PLAN[effective_plan(user)]


def alert_refresh_interval_for(user: User) -> timedelta:
    return ALERT_REFRESH_INTERVAL[effective_plan(user)]


def alert_detail_allowed(user: User) -> bool:
    return effective_plan(user) in PLANS_WITH_ALERT_DETAIL


def crop_change_alert_allowed(user: User) -> bool:
    return effective_plan(user) in PLANS_WITH_CROP_CHANGE_ALERT


def crop_suggestion_allowed(user: User) -> bool:
    return effective_plan(user) in PLANS_WITH_CROP_SUGGESTION


def marketplace_access_allowed(user: User) -> bool:
    return effective_plan(user) in PLANS_WITH_MARKETPLACE_ACCESS


def merchant_contact_visibility_allowed(user: User) -> bool:
    return effective_plan(user) in PLANS_WITH_MERCHANT_CONTACT_VISIBILITY
