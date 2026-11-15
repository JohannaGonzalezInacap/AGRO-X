import time
from threading import Lock
from typing import Any


class TTLCache:
    """Caché en memoria con vencimiento, por proceso (mismo patrón que `rate_limit.py`).

    Limitación conocida: con varias instancias de la API, cada una tiene su propia caché. Aceptable
    para el alcance de la hackathon; se revisa en la Fase 10 si el despliegue usa más de una.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        with self._lock:
            self._store[key] = (time.monotonic() + ttl_seconds, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
