# ADR-005 — Datos de la NASA y fuente de pronóstico

- Estado: Propuesta (fuente de pronóstico propuesta como Open-Meteo, falta aprobación del equipo)
- Fecha: 2026-11-14

## Contexto
El reto exige usar observaciones de la Tierra de la NASA. La idea del equipo exige alertar con
anticipación. Las fuentes de la NASA entregadas para el reto son de observación, no de pronóstico.

## Decisión
- Fuente NASA inicial: POWER (clima y agroclimatología), porque no pide clave y responde por punto.
- Segunda fuente NASA: SMAP para humedad de suelo, cuando POWER esté funcionando.
- Pronóstico: una fuente aparte, detrás de una interfaz propia para poder cambiarla.
- Cada alerta guarda qué fuentes usó, para poder explicarla.

## Fuente de pronóstico (propuesta, falta aprobar)

**Open-Meteo**, por estos criterios:

| Criterio | Resultado |
|---|---|
| Cobertura en Chile | Sí (modelos globales como GFS, ICON, ECMWF; no depende de redes de estaciones locales) |
| Días de anticipación | Hasta 16 días de pronóstico diario y horario |
| Costo para desarrollo/demo | Gratis, sin clave, hasta 10 000 llamadas/día (uso no comercial) |
| Costo para producción con cobro a usuarios | De pago (plan "API Standard"): endpoint dedicado con clave, sin límite diario, 1 000 000 de llamadas/mes. Precio exacto no publicado en dólares; confirmar con el proveedor |
| Licencia de los datos | CC BY 4.0: exige atribución visible donde se muestren los datos |

**Pendiente de decidir (no lo resuelve el agente):**
- [COMPLETAR: CONFIRMAR CONTRATACIÓN DEL PLAN DE PAGO DE OPEN-METEO ANTES DE COBRAR A USUARIOS REALES — el plan free es solo para desarrollo/demo de la hackathon] //Aqui tomaremos la decisión mas adelante
- Dónde poner la atribución CC BY 4.0 exigida por la licencia (por ejemplo, en la respuesta de la API o en la documentación pública).

**Alternativas consideradas:**
- OpenWeatherMap: cifras de precio y límites inconsistentes entre fuentes de terceros al momento de revisar (nov-2026); la página oficial de precios no se pudo confirmar en esta sesión. Descartada por ahora por esa falta de certeza.
- Dirección Meteorológica de Chile (oficial): no se encontró una API pública y documentada para consumo programático; solo servicios comerciales a medida, sin precios públicos.

## Consecuencias
- En la presentación hay que decirlo claro: NASA aporta el estado del campo y el clima histórico;
  el pronóstico viene de otra fuente.
- Los umbrales de riesgo (por ejemplo, a qué temperatura hay helada para cada cultivo) necesitan
  fuente agronómica. Sin fuente, se marcan como Ilustrativos.
