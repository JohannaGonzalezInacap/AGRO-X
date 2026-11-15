# Contrato de la API — v1

Estado: Propuesta. Todas las rutas van bajo `/v1`. La Fase 1 genera además el documento OpenAPI.

## Reglas generales

- Autenticación: cabecera `Authorization: Bearer <token de acceso>`.
- Formato: JSON. La entrada rechaza campos no declarados.
- Identificadores: UUID.
- Fechas: ISO 8601 en UTC.

## Formato único de error

```json
{ "error": { "code": "plan_required", "message": "Texto para la persona", "request_id": "uuid" } }
```

| HTTP | `code` | Cuándo |
|---|---|---|
| 401 | `unauthorized`, `invalid_credentials`, `invalid_refresh_token` | Sin sesión válida |
| 403 | `forbidden` | El rol no tiene acceso |
| 403 | `plan_required` | El plan no incluye la función |
| 404 | `not_found` | No existe o no es tuyo (misma respuesta en ambos casos) |
| 409 | `email_taken`, `conflict` | Dato duplicado |
| 413 | `payload_too_large` | Cuerpo demasiado grande |
| 422 | `validation_error` | Datos inválidos (indica el campo, no el valor) |
| 429 | `rate_limited`, `too_soon` | Demasiadas solicitudes o alerta pedida antes de tiempo |
| 502 | `upstream_unavailable` | Falló una fuente externa |
| 500 | `internal_error` | Error no previsto, sin detalles |

## Rutas

| Método y ruta | Quién | Qué hace |
|---|---|---|
| GET `/healthz` | Público | Estado del servicio |
| POST `/auth/register` | Público | Crea cuenta (productor o comerciante) |
| POST `/auth/login` | Público | Entrega token de acceso y de renovación |
| POST `/auth/refresh` | Público | Cambia el token de renovación por uno nuevo |
| POST `/auth/logout` | Público | Cierra la sesión |
| GET `/auth/me` | Con sesión | Perfil propio |
| POST `/farms` | Productor | Crea parcela |
| GET `/farms` | Productor | Lista sus parcelas |
| GET, PATCH, DELETE `/farms/{id}` | Dueño | Ver, editar, borrar |
| POST, GET `/farms/{id}/crop-history` | Dueño | Historial de cultivos. `POST` registra el cultivo de la temporada actual (`cultivo`, `fecha_plantacion`, `etapa_actual`) y vuelve no vigente al anterior |
| PATCH `/farms/{id}/crop-history/current` | Dueño | Cambia solo la `etapa_actual` del cultivo vigente (ej. de `floracion` a `fruto`), sin crear un historial nuevo |
| GET `/crops` | Con sesión | Catálogo de cultivos |
| POST `/farms/{id}/rotation/recommendations` | Dueño | Recomienda rotación según prioridades |
| POST `/farms/{id}/alerts/refresh` | Dueño | Recalcula alertas (frecuencia según plan) |
| GET `/farms/{id}/alerts` | Dueño | Alertas activas (detalle según plan) |
| GET `/farms/{id}/promotions/ideas` | Dueño, pro | Ideas de promoción |
| PUT `/marketplace/merchant-profile` | Comerciante | Crea o actualiza su perfil |
| GET `/marketplace/merchants` | Productor pro | Lista comerciantes |
| POST `/marketplace/surplus` | Productor pro | Publica merma |
| GET `/marketplace/surplus` | Comerciante, dueño | Lista mermas |
| PATCH `/marketplace/surplus/{id}` | Dueño | Cambia estado |
| GET `/billing/plans` | Público | Planes y precios |
| POST `/billing/checkout` | Con sesión | Inicia pago y devuelve la URL de la pasarela |
| GET `/billing/subscription` | Con sesión | Plan vigente |
| POST `/billing/webhooks/{provider}` | Pasarela | Aviso de pago (firma verificada) |
| GET `/privacy/export` | Con sesión | Descarga sus datos |
| DELETE `/privacy/account` | Con sesión | Elimina su cuenta y datos |
| GET, PUT `/privacy/consents` | Con sesión | Ver y cambiar consentimientos |
