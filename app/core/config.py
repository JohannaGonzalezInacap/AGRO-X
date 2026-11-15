from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    cors_origins: str = "http://localhost:5173"
    allowed_hosts: str = "localhost,127.0.0.1"
    max_body_bytes: int = 1_048_576

    database_url: str = "sqlite:///./dev.db"

    jwt_secret: str  # obligatorio: sin valor por defecto, para que falte ruidosamente, no en silencio
    jwt_issuer: str = "agro-xpace-api"
    jwt_audience: str = "agro-xpace-clients"
    access_token_minutes: int = 15
    refresh_token_days: int = 14

    # Límite de intentos por IP (ADR-002). En memoria y por proceso: ver ADR-002, Consecuencias.
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 60

    # Fuentes de datos externas (ADR-005, ADR-009).
    nasa_power_base_url: str = "https://power.larc.nasa.gov"
    forecast_base_url: str = "https://api.open-meteo.com"
    external_api_timeout_seconds: float = 10.0
    external_api_cache_ttl_seconds: int = 3600
    coordinate_rounding_decimals: int = 2

    # Job programado de recálculo de alertas (Fase 6). Revisa cada N minutos qué parcelas ya
    # pueden recalcular según la frecuencia de su plan (app/core/plans.py).
    alerts_job_interval_minutes: int = 60

    # Pagos (ADR-003). "fake" en desarrollo y pruebas; "mercadopago" para el adaptador real en
    # modo de pruebas. La pasarela simulada está prohibida en producción.
    payment_provider: str = "fake"
    payment_webhook_secret: str = ""
    mercadopago_access_token: str = ""
    mercadopago_api_base_url: str = "https://api.mercadopago.com"
    public_base_url: str = "http://localhost:8000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
