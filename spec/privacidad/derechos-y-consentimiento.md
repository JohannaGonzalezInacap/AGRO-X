# Derechos del titular y consentimiento

Estado: Propuesta. Se implementa en la Fase 9. Plazos y detalles legales por validar.

## Derechos y cómo se atienden

| Derecho | Cómo se atiende |
|---|---|
| Acceso | `GET /v1/privacy/export` entrega todos sus datos |
| Rectificación | Edición de perfil, parcelas y perfil de comerciante |
| Supresión | `DELETE /v1/privacy/account` elimina cuenta y datos asociados |
| Portabilidad | La exportación va en formato JSON |
| Oposición o retiro de consentimiento | `PUT /v1/privacy/consents` |
| Reclamos | Canal de contacto publicado (por definir) |

## Consentimientos

| Consentimiento | Cuándo se pide | Efecto de retirarlo |
|---|---|---|
| Publicar perfil de comerciante en el listado | Al crear el perfil | Deja de aparecer |
| Publicar contacto en una merma | Al publicar la merma | Se oculta el contacto |
| Recibir comunicaciones promocionales | Opcional, nunca marcado por defecto | No se envían |

## Reglas

1. Cada consentimiento se guarda con fecha y versión del texto aceptado.
2. Retirarlo es tan fácil como darlo.
3. Aceptar los términos del servicio no equivale a consentir publicidad.
4. Al eliminar la cuenta se borran o anonimizan los datos, salvo lo que la ley obligue a conservar.

## Pendiente

- [ ] Redactar política de privacidad y términos de uso.
- [ ] Definir canal de contacto y responsable de responder.
- [ ] Confirmar plazos legales de respuesta.
