# ADR-003 — Integración de pagos

- Estado: Propuesta
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
