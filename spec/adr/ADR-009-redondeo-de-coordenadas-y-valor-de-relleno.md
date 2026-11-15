# ADR-009 — Redondeo de coordenadas y valor de relleno de NASA POWER

- Estado: Aceptada
- Fecha: 2026-11-14

## Contexto
`spec/contratos/fuentes-datos.md` exige redondear las coordenadas antes de enviarlas a cualquier
fuente externa ("regla 4"), y tratar el valor de relleno de un día sin dato como "sin dato", no
como número. Ninguno de los dos queda con un valor exacto: no se dice a cuántos decimales redondear,
ni cuál es el valor de relleno de NASA POWER.

## Decisión
- Coordenadas: redondeo a **2 decimales** (~1,1 km de margen en latitud). Alcanza para clima y
  agroclimatología sin acercarse a identificar la parcela exacta.
- Valor de relleno de NASA POWER: **-999**. Es el valor documentado por ese proveedor para "sin
  dato" en sus parámetros diarios; cualquier lectura igual o menor a -990 se trata como `None`, no
  como número (deja margen para variantes como -999.0 o -9999 sin tener que listar cada una).

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| 2 decimales (elegida) | Suficiente para clima; simple | — |
| 4 decimales (~11 m) | Más preciso para el pronóstico | Innecesario para clima; más cerca de identificar la parcela |
| 0 o 1 decimal | Menos preciso, más privado | Puede alejar demasiado el punto de la parcela real en zonas con microclima |

## Consecuencias
- `app/integrations/nasa_power.py` y `app/integrations/forecast.py` comparten esta regla de
  redondeo antes de llamar a cualquier proveedor.
- Si más adelante un proveedor nuevo usa otro valor de relleno, se documenta ahí mismo en su
  cliente, no se asume -999 para todos.

## Documentos relacionados
- `spec/contratos/fuentes-datos.md` (reglas 3 y 4)
- ADR-005 (fuentes de datos)
- ADR-007 (mismo patrón: fijar un valor que el NFR dejaba abierto)
