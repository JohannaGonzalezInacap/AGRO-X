# ADR-011 — Umbrales del motor de riesgo (helada, calor, sequía, lluvia intensa)

- Estado: Aceptada
- Fecha: 2026-11-15

## Contexto
`spec/bdd/alertas.feature` exige detectar 4 tipos de riesgo (dominio.md regla 8), pero solo describe
2 con datos concretos (helada, sequía) y ninguno con números. Se investigó si alguna fuente de la
NASA o una API gratuita da umbrales agronómicos por cultivo (helada, calor, sequía) — no los da:
NASA POWER entrega observaciones crudas (temperatura, lluvia, humedad de suelo), no umbrales de
riesgo. Se revisó FAO Ecocrop (base retirada ~2015, sin API en vivo) y Meteoblue Crop Risk API (en
Beta, sin capa gratuita confirmada); ninguna es usable hoy sin trabajo de integración adicional.

## Decisión
- **Helada**: el umbral meteorológico de que haya helada (mínima ≤ 0 °C a 2 m) es una convención
  real y citable, no inventada. El ajuste según la tolerancia del cultivo (`frost_tolerance` del
  catálogo) sí es ilustrativo:
  - Tolerancia baja: alerta si la mínima pronosticada ≤ 2 °C.
  - Tolerancia media: ≤ 0 °C.
  - Tolerancia alta: ≤ -2 °C.
- **Calor extremo**: mismo patrón, con `heat_tolerance` (ilustrativo):
  - Tolerancia baja: alerta si la máxima pronosticada ≥ 30 °C.
  - Tolerancia media: ≥ 33 °C.
  - Tolerancia alta: ≥ 36 °C.
- **Sequía**: humedad de suelo observada (`GWETROOT`, NASA POWER) bajo **0.25** en los últimos 7
  días, y menos de **5 mm** de lluvia pronosticada en los próximos 7 días (ilustrativo).
- **Lluvia intensa**: pronóstico de **25 mm o más en un solo día** dentro de los próximos 7 días
  (ilustrativo).
- Todos estos umbrales (salvo el de helada de 0 °C) se marcan `illustrative: true` en la respuesta
  de la alerta, igual que el catálogo de cultivos (Fase 5) — no se presentan como si vinieran de
  una fuente agronómica real.
- Se usan **datos dummy a propósito** (decisión explícita de Joha, 2026-11-15): el MVP debe quedar
  funcional ahora; si el proyecto avanza, se conecta a una fuente agronómica real (Ecocrop con
  datos verificados a mano, o una API comercial) y este ADR se reemplaza, no se edita en silencio.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Umbrales fijos por tolerancia (elegida) | Simple, reutiliza el catálogo ya construido | Ilustrativo, no validado agronómicamente |
| FAO Ecocrop (valores reales, a mano) | Fuente real y citable | Requiere verificar manualmente cada valor por cultivo; riesgo de copiar mal un dato y presentarlo como "con fuente" sin estarlo de verdad |
| Meteoblue Crop Risk API | Pensado exactamente para esto | Beta inestable, sin capa gratuita confirmada, agrega una fuente externa nueva a mitad de la hackathon |

## Consecuencias
- Cuando el equipo consiga una fuente agronómica real (pendiente desde la Fase 0), este ADR se
  reemplaza y el catálogo deja de salir marcado ilustrativo.
- El umbral de 0 °C para "hay helada" en términos meteorológicos generales no cambia aunque se
  reemplace este ADR; lo que cambia es el ajuste por tolerancia de cultivo.

## Documentos relacionados
- `spec/bdd/alertas.feature`, ADR-005, ADR-008, ADR-009, ADR-010
