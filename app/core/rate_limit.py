import time
from collections import defaultdict
from threading import Lock

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import AppError


class InMemoryRateLimiter:
    """Ventana deslizante por clave (IP + acción), en memoria y por proceso.

    Limitación conocida (ADR-002, Consecuencias): con varias instancias de la API, cada una
    cuenta por su cuenta. Aceptable para el alcance de la hackathon (una sola instancia);
    se revisa en la Fase 10 si el despliegue final usa más de una.
    """

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def hit(self, key: str, max_attempts: int, window_seconds: int) -> None:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            attempts = [t for t in self._hits[key] if t > cutoff]
            if len(attempts) >= max_attempts:
                self._hits[key] = attempts
                raise AppError(429, "rate_limited", "Demasiados intentos. Espera un momento.")
            attempts.append(now)
            self._hits[key] = attempts

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


login_rate_limiter = InMemoryRateLimiter()


def enforce_login_rate_limit(request: Request, action: str) -> None:
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    login_rate_limiter.hit(
        key=f"{action}:{client_ip}",
        max_attempts=settings.login_rate_limit_attempts,
        window_seconds=settings.login_rate_limit_window_seconds,
    )
