from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.middleware import (
    BodySizeLimitMiddleware,
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
)
from app.jobs.alerts_job import start_alerts_scheduler, stop_alerts_scheduler
from app.modules.alerts.router import router as alerts_router
from app.modules.auth.router import router as auth_router
from app.modules.billing.router import router as billing_router
from app.modules.farms.router import router as farms_router
from app.modules.rotation.router import router as rotation_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    start_alerts_scheduler()
    yield
    stop_alerts_scheduler()


app = FastAPI(title="AGRO-X API", lifespan=lifespan)

# El orden importa: Starlette ejecuta el último middleware agregado primero. Queremos que
# RequestIdMiddleware corra antes que todo lo demás, para que cualquier error (incluido
# BodySizeLimitMiddleware) ya tenga un request_id disponible.
app.add_middleware(BodySizeLimitMiddleware, max_bytes=settings.max_body_bytes)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIdMiddleware)

register_error_handlers(app)
app.include_router(auth_router)
app.include_router(farms_router)
app.include_router(rotation_router)
app.include_router(alerts_router)
app.include_router(billing_router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
