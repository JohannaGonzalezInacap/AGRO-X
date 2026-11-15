# Fuentes de datos externas

Estado: Propuesta. NASA POWER ya se probó con una llamada real (ver abajo). El resto sigue sin probar.

## Idea central

| Tipo | Qué dice | Ejemplo | Sirve para |
|---|---|---|---|
| Observación | Cómo está y cómo ha estado el campo | NASA POWER, SMAP, IMERG | Rotación, sequía, contexto climático |
| Pronóstico | Cómo estará en los próximos días | Fuente por elegir (ADR-005) | Alertar con tiempo |

Los datos de la NASA de esta lista son de observación. Sin una fuente de pronóstico no hay alerta
anticipada.

## Orden de integración

| Prioridad | Fuente | Para qué | Notas |
|---|---|---|---|
| 1 | NASA POWER | Temperatura, lluvia, humedad de suelo, climatología | No pide clave. Es la más simple |
| 1 | Fuente de pronóstico | Mínimas, máximas y lluvia de los próximos días | Revisar licencia de uso comercial |
| 2 | SMAP | Humedad de suelo más precisa | Pide cuenta de Earthdata |
| 2 | Suelo local | Textura, drenaje, materia orgánica | SSURGO y Web Soil Survey solo cubren EE. UU.; para Chile buscar fuente local o que el productor lo ingrese |
| 3 | Landsat, MODIS o Sentinel-2 | Vigor del cultivo (NDVI) | Más complejo; dejar para después |
| 3 | Precios de mercado | Componente de ingreso en la rotación | USDA cubre EE. UU.; para Chile buscar fuente local |

## NASA POWER — llamada de prueba

Pega esta dirección en el navegador. Debe devolver datos diarios de Santiago:

```
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR&community=AG&longitude=-70.65&latitude=-33.45&start=20261101&end=20261107&format=JSON
```

Parámetros a confirmar en la documentación oficial (https://power.larc.nasa.gov/docs/):

| Parámetro | Significado esperado |
|---|---|
| `T2M_MAX`, `T2M_MIN` | Temperatura máxima y mínima a 2 metros (°C) |
| `PRECTOTCORR` | Precipitación corregida (mm por día) |
| `GWETROOT` | Humedad del suelo en zona de raíces (0 a 1) |

Datos a tener en cuenta: el límite es de 20 parámetros por consulta de un punto; los días más
recientes pueden venir sin dato (valor de relleno), y eso hay que tratarlo como "sin dato", no como
número.

**Verificado el 2026-11-14:** la llamada devolvió JSON válido con `T2M_MAX`, `T2M_MIN` y
`PRECTOTCORR` diarios para Santiago (ejemplo: 01-11-2026, T2M_MAX 19.14 °C, T2M_MIN 6.45 °C,
PRECTOTCORR 0.12 mm/día), sin valores de relleno en ese rango.

## Reglas para todo cliente externo

1. Dirección base fija en la configuración.
2. Tiempo de espera máximo y manejo de error con `upstream_unavailable`.
3. Caché, para no repetir consultas y respetar los límites del proveedor.
4. Coordenadas redondeadas; nunca enviar datos de la persona.
5. Pruebas con respuestas simuladas; ninguna prueba automática depende de internet.
6. Cada proveedor nuevo se anota en `gobierno/proveedores.md`.
