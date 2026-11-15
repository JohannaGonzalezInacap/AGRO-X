# ADR-013 — Ideas de venta urgente ante una alerta de riesgo alto

- Estado: Aceptada
- Fecha: 2026-11-15

## Contexto

`spec/alcance-y-planes.md` incluía desde el inicio una fila "Ideas de promoción" sin alcance
definido. En la Fase 8 se dejó **en pausa** (`@en-pausa` en `spec/bdd/alertas.feature`) porque no
estaba claro qué debía hacer.

Joha aclaró el alcance real (2026-11-15): no es un motor de marketing general para toda la cosecha
("no estoy construyendo un SaaS"). Es algo puntual: cuando una parcela tiene una **alerta de riesgo
alto** (helada, calor extremo, sequía o lluvia intensa con `severity = "alta"`, motor de riesgo de
la Fase 6), avisar al productor que puede estar a punto de perder su cultivo, y sugerirle de forma
creativa y realista cómo vender o aprovechar esa cosecha antes de perderla por el clima.

En la misma conversación, Joha decidió pausar el marketplace de comerciantes y mermas construido en
la Fase 8 (ver ND-002 en `DECISIONES.md`) porque no está claro qué tan provechoso es. Esta función
**no depende de ese marketplace**: no referencia mermas ni comerciantes, para no quedar bloqueada si
ese módulo se retira más adelante.

## Decisión

- Nuevo endpoint `GET /farms/{farm_id}/promotions/ideas` (rol productor, dueño de la parcela).
- Solo devuelve contenido si la parcela tiene al menos una alerta **activa** con `severity = "alta"`
  (mismo criterio que ya calcula el motor de riesgo de la Fase 6, sin fuente de mercado nueva). Si
  no hay ninguna, responde 404 `not_found` — no se fabrica una idea de venta sin un riesgo real.
- Requiere plan **básico o pro** (`PLANS_WITH_PROMOTION_IDEAS` en `app/core/plans.py`), el mismo
  umbral que ya existe para ver el detalle de una alerta (ADR-006): esta función necesita leer ese
  detalle (tipo de alerta, cultivo vigente), así que no tiene sentido ofrecerla a quien no ve el
  detalle. Un plan pro vencido se comporta como free (regla general de `effective_plan`).
- El contenido se arma a partir del tipo de alerta y el cultivo vigente de la parcela (si lo hay);
  son sugerencias **ilustrativas** (`illustrative: true`), no datos de mercado reales — no existe
  todavía una fuente de precios o canales de venta confirmada.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Atada a alerta de severidad alta (elegida) | Responde a un riesgo real y vigente; reusa el motor de alertas sin tabla nueva | No cubre venta planeada sin riesgo climático |
| Disponible para cualquier severidad | Más casos cubiertos | Genera ruido y falsas urgencias; no es lo que se pidió |
| Motor de marketing general (todo cultivo, en cualquier momento) | Más "completo" | Explícitamente descartado por Joha: no es el alcance de este proyecto |
| Ligarlo al marketplace de mermas (Fase 8) | Reusaría ese módulo | Ese módulo queda en pausa (ND-002); esta función no debe depender de algo pausado |

## Consecuencias

- `spec/alcance-y-planes.md`: la fila "Ideas de promoción" se reemplaza por "Ideas de venta urgente
  (alerta de riesgo alto)", disponible en básico y pro.
- Nuevo módulo `app/modules/promotions/` (sin tabla propia: lee `Alert` y `CropHistory` que ya
  existen).
- `spec/bdd/alertas.feature` pierde el escenario `@en-pausa`; los escenarios de esta función viven
  en `spec/bdd/promociones.feature` (nuevo).
- Si el equipo decide retirar el marketplace de mermas, esta función sigue funcionando igual.

## Documentos relacionados

- `spec/alcance-y-planes.md` (tabla de planes)
- `spec/bdd/promociones.feature` (escenarios BDD)
- ADR-011 (umbrales del motor de riesgo, de donde viene `severity`)
- ADR-006 (control de acceso por plan)
- `DECISIONES.md` ND-002 (pausa del marketplace de mermas)
