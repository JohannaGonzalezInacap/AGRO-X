# ADR-012 — Precio de desarrollo para básico y pro, mientras no hay precio real

- Estado: Aceptada
- Fecha: 2026-11-15

## Contexto
`spec/alcance-y-planes.md` deja el precio de básico y pro como "Por definir" (decisión abierta del
equipo). Pero `spec/bdd/pagos.feature` exige que se pueda iniciar un pago de "basic" y que el
webhook compare "el monto correcto" contra el plan — sin un monto, ese flujo no se puede probar ni
funcionar de verdad.

## Decisión
- Se usa un **precio de desarrollo** (placeholder, no es el precio final): básico 9.990 CLP/mes,
  pro 19.990 CLP/mes. Vive solo en `app/modules/billing/service.py`, en una constante con un
  comentario que apunta a este ADR.
- **El catálogo público (`GET /billing/plans`) nunca muestra este número como si fuera el precio
  real** — devuelve `price: null` y `price_defined: false` para ambos planes, igual que ya estaba
  decidido. El placeholder solo se usa internamente para que el cobro y la verificación de monto
  funcionen de punta a punta.
- Cuando el equipo fije el precio real (pendiente de la Fase 0), se reemplaza esa constante y este
  ADR se marca reemplazado — no se cambia en silencio.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Precio de desarrollo interno, catálogo público en null (elegida) | El flujo de pago se puede construir y probar ya | Hay un número en el código que no es el precio real; riesgo de que alguien lo use por error como si lo fuera si no se documenta bien |
| Dejar el monto como `None` en todo el flujo | Nada que inventar | El webhook no podría verificar "monto correcto" (regla central de ADR-003 y PCI); rompe el escenario "Monto distinto al esperado" |
| Bloquear la Fase 7 hasta tener el precio real | Cero datos inventados | El equipo no pidió bloquear; "no detener el avance" es la regla por defecto de `CLAUDE.md` para esto |

## Consecuencias
- Si alguien compra básico o pro hoy, se le cobraría (en un entorno real) el placeholder, no un
  precio aprobado — por eso el proveedor real de Mercado Pago (`providers/mercadopago.py`) todavía
  no implementa `create_checkout` de verdad (ver su código): no se puede cobrar dinero real con un
  precio que nadie aprobó.
- Esto no bloquea probar el flujo completo con la pasarela simulada.

## Documentos relacionados
- `spec/alcance-y-planes.md`, ADR-003, `spec/bdd/pagos.feature`
