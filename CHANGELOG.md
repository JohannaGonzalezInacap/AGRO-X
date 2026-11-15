# Historial de cambios

Lo más nuevo arriba. Una entrada por fase cerrada o por despliegue.

## [Sin publicar]

### Agregado
- 2026-11-14: Fase 5 — Rotación de cultivos (núcleo del reto): `GET /crops` (catálogo) y
  `POST /farms/{id}/rotation/recommendations`. Motor de puntaje con 3 reglas probadas en
  `spec/bdd/rotacion.feature` (reposición de nitrógeno, evitar repetir familia, baja demanda de
  agua con poca disponibilidad), siempre con al menos una razón por cultivo y las fuentes de datos
  usadas. Catálogo inicial sembrado por migración (8 cultivos, todos sin fuente agronómica todavía
  → `illustrative: true`). ADR-010 (umbral de "baja precipitación", 14 días / 2 mm/día).
- 2026-11-14: Fase 4 — Fuentes de datos: cliente de NASA POWER (`app/integrations/nasa_power.py`)
  y de pronóstico Open-Meteo (`app/integrations/forecast.py`). Caché en memoria con vencimiento
  (`app/core/cache.py`), tiempo de espera configurable, valor de relleno de NASA POWER (-999)
  tratado como dato faltante, coordenadas redondeadas a 2 decimales (ADR-009). Sin rutas nuevas:
  son los clientes que usarán las Fases 5 y 6.
- 2026-11-14: Fase 3 — Parcelas e historial de cultivos: `POST/GET /farms`,
  `GET/PATCH/DELETE /farms/{id}`, `POST/GET /farms/{id}/crop-history`,
  `PATCH /farms/{id}/crop-history/current`. Tope de parcelas por plan (`app/core/plans.py`, fuente
  en `spec/alcance-y-planes.md`), aislamiento por dueño (404 si no es tuya o no existe), como
  máximo un cultivo vigente por parcela. Rol "productor" obligatorio (`require_role`, agregado a
  `app/modules/auth/service.py`). Nueva migración de Alembic (`farms`, `crop_history`).
  `spec/bdd/farms.feature` nuevo.
- 2026-11-14: Fase 2 — Cuentas y acceso: `POST /auth/register`, `POST /auth/login`,
  `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me`. Contraseñas con Argon2id, token de
  acceso JWT (15 min), token de renovación opaco de un solo uso con revocación de toda la cadena si
  se reutiliza, límite de intentos por IP, registro de auditoría. Primera migración de Alembic
  (`users`, `refresh_tokens`, `audit_log`). ADR-002 aceptado.
- 2026-11-14: ADR-008 — alerta de cambio de cultivo (básico sin sugerencia, pro con sugerencia de
  rotación); no implementada todavía, queda para las Fases 5 y 6.
- 2026-11-14: Fase 1 — esqueleto de la API (FastAPI), `GET /healthz`, formato único de error,
  cabeceras de seguridad, límite de tamaño de cuerpo, CORS y hosts permitidos con lista cerrada,
  primeras pruebas, revisión automática en `.github/workflows/ci.yml`.
- 2026-11-14: estructura de carpetas, documentación inicial en `spec/`, `CLAUDE.md` y `RUTA.md`.
