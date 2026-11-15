# ADR-014 — Exportar datos, eliminar cuenta y consentimientos

- Estado: Aceptada
- Fecha: 2026-11-15

## Contexto

`spec/privacidad/derechos-y-consentimiento.md` y `spec/privacidad/retencion-y-borrado.md` ya
describían qué derechos atender y qué pasa con cada dato al eliminar una cuenta, pero nada estaba
construido (Fase 9, `RUTA.md`). Hacía falta decidir el detalle de implementación: qué incluye
exactamente la exportación, qué se borra y qué solo se anonimiza, y qué tan amplio es el sistema de
consentimientos.

## Decisión

- `GET /privacy/export`: devuelve en un solo JSON todo lo que el usuario puede ver de sí mismo —
  perfil, parcelas con su historial de cultivo y sus alertas (activas e inactivas), perfil de
  comerciante y mermas propias (según el rol), pagos y consentimientos. No incluye el hash de la
  contraseña ni el de los tokens de sesión (nadie los ve, ni siquiera el titular, igual que hoy).
- `DELETE /privacy/account`: borra la cuenta y lo que le pertenece —
  - Se **borran**: parcelas, historial de cultivo, alertas, perfil de comerciante, mermas propias,
    consentimientos, tokens de renovación (regla 1 de `retencion-y-borrado.md`: nada personal activo
    queda).
  - Se **anonimizan** (se quita el vínculo con la persona, no se borra el registro): pagos
    (`Payment.user_id` pasa a `NULL` — exige volver esa columna nullable) y auditoría
    (`AuditLog.user_id` ya era `NULL`-able), según la tabla de retención ("pagos: se anonimiza el
    vínculo" y necesidades contables/de seguridad).
- `GET, PUT /privacy/consents`: por ahora cubre un solo consentimiento real y autónomo —
  "comunicaciones promocionales" (ND-003 abajo). Los otros dos de la tabla original ("publicar
  perfil de comerciante", "publicar contacto en una merma") ya están gobernados por datos propios
  de `app/modules/marketplace/` (crear o borrar el perfil; marcar `contact_visible` en una merma) y
  no se duplican aquí — tener dos lugares que dicen si algo está "consentido" sería una segunda
  fuente de verdad.
- Registros sin datos personales: ya se cumplía (`app/jobs/alerts_job.py` es el único `logger` del
  proyecto y no registra nada personal); no hizo falta cambiar nada para este punto de la Fase 9.
- Métricas para los indicadores (`spec/mejora-continua/indicadores.md`): por ahora solo se asegura
  que exportar datos, eliminar cuenta y cambiar un consentimiento queden en `AuditLog`, para que el
  indicador "Solicitudes de privacidad en plazo" tenga de dónde salir. Un tablero en vivo para el
  resto de los indicadores (disponibilidad, tiempo de respuesta, etc.) es trabajo de observabilidad
  de infraestructura, no de esta API — queda para la Fase 10 si se alcanza a montar.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Un solo consentimiento real, los otros dos gobernados por su propio módulo (elegida) | Una sola fuente de verdad por dato; menos tablas | No sigue la tabla original al pie de la letra |
| Los tres consentimientos en la tabla `consents` | Sigue la spec original tal cual | Duplica estado con `marketplace` (perfil existe / `contact_visible`); ese módulo además está en pausa (ND-002) |
| Borrar también los pagos | Más simple de implementar | Contradice `retencion-y-borrado.md` y probablemente una obligación tributaria |

## Consecuencias

- `app/modules/billing/models.py`: `Payment.user_id` pasa a nullable (migración nueva).
- Nuevo módulo `app/modules/privacy/` (`Consent`, servicio, rutas), sin depender del marketplace.
- `spec/privacidad/derechos-y-consentimiento.md` se actualiza para reflejar el alcance real (ND-003)
  y la ruta correcta (`/privacy/...`, sin `/v1`, igual que el resto de la API — `api-v1.md` ya lo
  tenía bien en su tabla de rutas, solo este documento tenía el prefijo viejo).

## Documentos relacionados

- `spec/privacidad/derechos-y-consentimiento.md`
- `spec/privacidad/retencion-y-borrado.md`
- `spec/privacidad/inventario-datos.md`
- `spec/bdd/privacidad.feature`
- `DECISIONES.md` ND-003
