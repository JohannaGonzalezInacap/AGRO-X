# ADR-003 — Integración de pagos

- Estado: Aceptada
- Fecha: 2026-11-14

## Contexto
Los planes básico y pro se pagan. Manejar tarjetas directamente obliga a cumplir PCI DSS completo,
algo fuera del alcance del equipo.

## Decisión
- Pago por redirección: la persona paga en la página de la pasarela. La API nunca recibe, guarda
  ni registra datos de tarjeta.
- Pasarela inicial: Mercado Pago (opera en Chile), en modo de pruebas.
- Patrón adaptador: cada pasarela es una clase en `billing/providers/` con la misma interfaz. Hay
  una pasarela simulada para desarrollo y pruebas, prohibida en producción.
- El plan cambia solo al recibir un webhook que cumple tres cosas: firma válida, aviso no
  procesado antes, y pago confirmado consultando a la pasarela con monto y moneda correctos.

## Alternativas consideradas
- Formulario de tarjeta propio: descartado por alcance PCI.
- Otras pasarelas chilenas (Webpay, Flow): posibles después gracias al adaptador.

## Consecuencias
- El alcance PCI se reduce al cuestionario más liviano (ver `seguridad/pagos-pci.md`).
- Hay que confirmar en la documentación vigente de la pasarela el formato exacto de firma y de las
  rutas antes de programar la Fase 7.
- Suscripción con cobro automático mensual queda fuera: cada pago activa 30 días.

## Implementación (Fase 7)
- Firma del webhook de Mercado Pago verificada contra su documentación vigente (2026-11-15):
  cabecera `x-signature` (`ts=...,v1=...`), `HMAC-SHA256` sobre
  `id:{data.id};request-id:{x-request-id};ts:{ts};`. Confirmación del pago: `GET /v1/payments/{id}`
  con `Bearer`. Los nombres de los campos de monto/moneda (`transaction_amount`, `currency_id`) no
  se confirmaron contra una respuesta real — mismo pendiente que ya tenía
  `spec/seguridad/pagos-pci.md`.
- El adaptador real de Mercado Pago (`app/modules/billing/providers/mercadopago.py`) todavía **no**
  puede iniciar un pago de verdad: falta la cuenta de pruebas (pendiente desde la Fase 0) y el
  precio real de los planes (ADR-012). Sí puede verificar firma y confirmar un pago, para cuando
  ambos existan.
- Pasarela simulada (`providers/fake.py`) para desarrollo y pruebas, con un endpoint de solo
  desarrollo para fijar el resultado que "confirmaría" (`POST /billing/_dev/fake-approve/...`),
  deshabilitado si `PAYMENT_PROVIDER` no es `fake`.
