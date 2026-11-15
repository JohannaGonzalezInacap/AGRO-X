# Derechos del titular y consentimiento

Estado: Implementado (Fase 9, ADR-014). Plazos y detalles legales por validar.

## Derechos y cómo se atienden

| Derecho | Cómo se atiende |
|---|---|
| Acceso | `GET /privacy/export` entrega todos sus datos |
| Rectificación | Edición de perfil, parcelas y perfil de comerciante |
| Supresión | `DELETE /privacy/account` elimina cuenta y datos asociados |
| Portabilidad | La exportación va en formato JSON |
| Oposición o retiro de consentimiento | `PUT /privacy/consents` |
| Reclamos | Canal de contacto publicado (por definir) |

## Consentimientos

**ND-003 (2026-11-15):** `GET, PUT /privacy/consents` solo administra el tercero de esta tabla.
Los otros dos ya los gobierna el propio `app/modules/marketplace/` (crear o borrar el perfil;
marcar `contact_visible` en una merma) — no se duplican en una tabla de consentimientos aparte.

| Consentimiento | Cuándo se pide | Efecto de retirarlo | Dónde vive |
|---|---|---|---|
| Publicar perfil de comerciante en el listado | Al crear el perfil | Deja de aparecer | Existencia del `MerchantProfile` |
| Publicar contacto en una merma | Al publicar la merma | Se oculta el contacto | `Surplus.contact_visible` |
| Recibir comunicaciones promocionales | Opcional, nunca marcado por defecto | No se envían | `GET, PUT /privacy/consents` |

## Reglas

1. Cada consentimiento se guarda con fecha y versión del texto aceptado.
2. Retirarlo es tan fácil como darlo.
3. Aceptar los términos del servicio no equivale a consentir publicidad.
4. Al eliminar la cuenta se borran o anonimizan los datos, salvo lo que la ley obligue a conservar.

## Pendiente

- [ ] Redactar política de privacidad y términos de uso.
- [ ] Definir canal de contacto y responsable de responder.
- [ ] Confirmar plazos legales de respuesta.
