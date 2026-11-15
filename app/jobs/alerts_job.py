import logging
from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.errors import AppError
from app.core.plans import alert_refresh_interval_for
from app.core.time import as_aware_utc
from app.modules.alerts.service import refresh_alerts
from app.modules.auth.models import User
from app.modules.farms.models import Farm

logger = logging.getLogger("app.jobs.alerts")

_scheduler: BackgroundScheduler | None = None


def run_due_refreshes() -> None:
    """Recalcula las alertas de toda parcela a la que ya le toque, según la frecuencia de su
    plan (RUTA.md, Fase 6). Si falla una parcela (502 de una fuente externa, por ejemplo), se
    registra y se sigue con las demás — no se detiene el job completo por una sola falla."""
    db = SessionLocal()
    try:
        farms = db.scalars(select(Farm)).all()
        for farm in farms:
            owner = db.get(User, farm.owner_id)
            if owner is None:
                continue
            interval = alert_refresh_interval_for(owner)
            if farm.alerts_refreshed_at is not None:
                next_allowed = as_aware_utc(farm.alerts_refreshed_at) + interval
                if datetime.now(UTC) < next_allowed:
                    continue
            try:
                refresh_alerts(db, owner, farm.id)
            except AppError as exc:
                logger.warning(
                    "No se pudo recalcular alertas de la parcela %s: %s", farm.id, exc.message
                )
                db.rollback()
    finally:
        db.close()


def start_alerts_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    settings = get_settings()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_due_refreshes,
        "interval",
        minutes=settings.alerts_job_interval_minutes,
        id="alerts_refresh",
    )
    scheduler.start()
    _scheduler = scheduler
    return scheduler


def stop_alerts_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
