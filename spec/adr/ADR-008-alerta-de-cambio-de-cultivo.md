# ADR-008 — Alerta de cambio de cultivo, diferenciada por plan

- Estado: Propuesta
- Fecha: 2026-11-14

## Contexto
Hasta ahora `spec/alcance-y-planes.md` solo diferenciaba por plan la frecuencia y el detalle de las
alertas **climáticas** (helada, calor, lluvia intensa, sequía). Falta una alerta distinta: avisar
que conviene cambiar el cultivo de la parcela (fin de temporada o etapa de cosecha), y que el plan
pro vea además **qué** cultivo conviene plantar a continuación, usando el motor de recomendación de
rotación (Fase 5, núcleo del reto).

## Decisión
- Nuevo tipo de alerta, distinto de los climáticos: `cambio_de_cultivo`. Se dispara cuando el
  cultivo vigente de la parcela llega a la etapa `cosecha` (ver `spec/dominio.md`, regla 13).
- **Básico y pro** reciben esta alerta. **Free no la recibe** (coherente con que free ya tiene
  menos frecuencia y detalle de alertas en ADR-006).
- Contenido según plan:
  - Básico: aviso de que conviene cambiar el cultivo, sin decir cuál.
  - Pro: el mismo aviso, más la sugerencia de qué cultivo plantar la siguiente temporada — llama al
    motor de recomendación de rotación (Fase 5) y devuelve su primera opción con sus razones.
- No dispara pago ni acción automática: es solo información para que la persona decida.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Alerta separada `cambio_de_cultivo` (elegida) | Reusa el motor de alertas y su frecuencia por plan (ADR-006); fácil de extender | Depende de que Rotación (Fase 5) ya exista cuando se calcule el detalle pro |
| Meterlo dentro de la respuesta de `POST /farms/{id}/rotation/recommendations` | No toca el módulo de alertas | No es una alerta: no se recalcula sola ni avisa proactivamente del fin de temporada |
| Que el básico también vea la sugerencia de cultivo | Más simple de implementar (una sola rama) | Contradice lo pedido: la sugerencia concreta es diferenciador de pro |

## Consecuencias
- El motor de alertas (Fase 6) pasa a depender del motor de rotación (Fase 5) para el detalle del
  plan pro. Rotación debe quedar lista antes de terminar Alertas, o Alertas debe tolerar que
  Rotación no tenga una recomendación disponible (fuera de catálogo, datos insuficientes) y mostrar
  el aviso sin sugerencia en ese caso.
- `spec/alcance-y-planes.md` y `spec/bdd/alertas.feature` se actualizan para incluir esta fila y un
  escenario nuevo.
- No afecta la Fase 2 (Cuentas y acceso): el plan ya se modela en `User.plan`, no hace falta ningún
  dato nuevo en esa fase.

## Documentos relacionados
- `spec/alcance-y-planes.md` (tabla de planes)
- `spec/bdd/alertas.feature` (escenario BDD)
- `spec/dominio.md` (tipos de alerta, etapa `cosecha`)
- ADR-006 (control de acceso por plan)
