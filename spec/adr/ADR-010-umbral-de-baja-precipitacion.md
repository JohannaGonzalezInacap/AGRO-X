# ADR-010 — Umbral de "baja precipitación" para la rotación

- Estado: Aceptada
- Fecha: 2026-11-14

## Contexto
`spec/bdd/rotacion.feature` (escenario "Con poca agua se prefieren cultivos de baja demanda") exige
distinguir cuándo "la zona es de baja precipitación", pero no da un número. Sin un valor concreto,
el motor de rotación no puede decidir cuándo aplicar esa regla.

## Decisión
- Se consultan los últimos **14 días** de observación de NASA POWER (`PRECTOTCORR`) para las
  coordenadas de la parcela.
- Si el promedio diario de esos días (ignorando los días sin dato, ADR-009) es **menor a 2 mm/día**,
  se considera "baja precipitación" para efectos de esta regla.
- Si no hay ningún día con dato en la ventana (todo vino como relleno), se trata como que **no** se
  puede afirmar baja precipitación (no se aplica la penalización, por falta de evidencia) y se anota
  en los avisos de la respuesta.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| 14 días, 2 mm/día (elegida) | Ventana corta, reacciona rápido a un período seco reciente | No distingue estación del año (una ventana de 14 días en invierno lluvioso podría no calificar como "seca" aun si la zona es árida en general) |
| Promedio histórico de la zona (climatología) | Más representativo del clima de largo plazo | Requiere más llamadas y un criterio de "normal para la zona" que tampoco está definido |
| 30 días, mismo umbral | Menos sensible a un corte de lluvia puntual | Tarda más en reflejar un cambio reciente, que es lo que le importa a quien está decidiendo qué plantar ahora |

## Consecuencias
- Si el equipo define más adelante un criterio climatológico por región, este ADR se reemplaza
  (no se edita en silencio — ver `registrar-decision`).
- El umbral vive en `app/modules/rotation/service.py` como constantes, no repartido en el código.

## Documentos relacionados
- `spec/bdd/rotacion.feature`
- ADR-005, ADR-009 (fuentes de datos y manejo de valores de relleno)
