from datetime import UTC, datetime

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
