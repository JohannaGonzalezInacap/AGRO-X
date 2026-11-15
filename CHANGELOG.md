# Historial de cambios

Lo más nuevo arriba. Una entrada por fase cerrada o por despliegue.

## [Sin publicar]

### Agregado
- 2026-11-15: Fase 8 — Comerciantes y mermas: `PUT /marketplace/merchant-profile`,
  `GET /marketplace/merchants`, `POST /marketplace/surplus`, `GET /marketplace/surplus`,
  `PATCH /marketplace/surplus/{id}`. Listar comerciantes y publicar mermas (lado productor) y ver
  el contacto de una merma (lado comerciante, ND-001) quedan limitados a plan pro. El contacto de
  una merma solo se muestra si el productor lo publicó y el comerciante que consulta es pro.
  `spec/bdd/marketplace.feature` nuevo. Quedan **en pausa** las "ideas de promoción" (decisión
  explícita de Joha: falta definir el alcance).
- 2026-11-15: Fase 7 — Planes y pagos: `GET /billing/plans`, `POST /billing/checkout`,
  `GET /billing/subscription`, `POST /billing/webhooks/{provider}`. Pasarela simulada (`fake`)
  para desarrollo y pruebas, y adaptador real de Mercado Pago en modo de pruebas (firma y
  confirmación verificadas contra su documentación vigente). Webhook con firma, idempotencia y
  verificación de monto/moneda antes de activar el plan (30 días); desajuste de monto queda en
  auditoría, no activa nada. Precios de básico/pro siguen como "por definir" en el catálogo
  público (ADR-012: se usa un precio de desarrollo solo internamente, nunca mostrado como real).
- 2026-11-15: Fase 6 — Alertas y control por plan: `POST /farms/{id}/alerts/refresh`,
  `GET /farms/{id}/alerts`. Motor de riesgo (helada, calor extremo, sequía, lluvia intensa) con
  umbrales ilustrativos (ADR-011; no hay fuente agronómica gratuita disponible, se investigó).
  Alerta de cambio de cultivo (ADR-008) integrada con el motor de rotación (Fase 5). Detalle y
  recomendaciones ocultos en plan free; límite de recálculo por plan (429 `too_soon`); si falla una
  fuente externa, las alertas anteriores siguen disponibles (502, sin perder nada). Job programado
  (`APScheduler`) que recalcula sola cada parcela según le toque por su plan.
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
