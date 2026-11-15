# ADR-007 — Cabeceras de seguridad y límites HTTP

- Estado: Propuesta
- Fecha: 2026-11-14

## Contexto
`spec/nfr.md` y `spec/seguridad/controles-aplicables.md` exigen cabeceras de seguridad y un límite
de tamaño de cuerpo desde la Fase 1, pero no fijan valores exactos. Queda como decisión técnica,
según la regla 6 de `CLAUDE.md`.

## Decisión
- Límite de tamaño de cuerpo: 1 MiB (`MAX_BODY_BYTES=1048576`), configurable por variable de
  entorno. Por encima, `413` con código `payload_too_large`.
- Cabeceras en toda respuesta:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: no-referrer`
  - `Permissions-Policy: geolocation=(), camera=(), microphone=()`
  - `Cache-Control: no-store` (salvo que una ruta futura la sobrescriba a propósito)
  - `X-Request-Id: <uuid>` (trazabilidad, pedida por `spec/nfr.md`)
- `Strict-Transport-Security` queda para la Fase 10 (se agrega en el borde HTTPS de la nube, no
  tiene sentido en HTTP local de desarrollo).
- CORS: lista cerrada de orígenes desde `CORS_ORIGINS`, nunca `*`.
- `TrustedHostMiddleware` con lista cerrada desde `ALLOWED_HOSTS`.

## Alternativas consideradas
- Dejar las cabeceras sueltas en cada ruta: se descarta, se olvidarían en rutas nuevas.
- 1 MiB de límite: valor Ilustrativo, razonable para JSON de formularios; se ajusta si una fase
  futura necesita subir archivos (no hay ninguna prevista en el alcance actual).

## Consecuencias
- Cualquier carga de archivos futura necesitará su propio límite, mayor a 1 MiB, documentado aquí.
- Las pruebas de la Fase 1 verifican estas cabeceras y el límite.
