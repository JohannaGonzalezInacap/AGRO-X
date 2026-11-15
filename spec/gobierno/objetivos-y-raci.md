# Objetivos y responsables (COBIT 2019)

Estado: Pendiente de nombres.

## Objetivos del proyecto

| Objetivo de negocio | Cómo se mide |
|---|---|
| Ayudar al productor a elegir rotaciones que cuiden suelo y agua | Recomendaciones entregadas con razones |
| Avisar con tiempo de riesgos climáticos | Días de anticipación de las alertas |
| Reducir pérdida de cosecha | Mermas publicadas y contactos generados |
| Operar sin incidentes de datos ni de pagos | Incidentes por mes |

## Objetivos de COBIT 2019 que aplican

| Objetivo | Tema | Documento |
|---|---|---|
| EDM03, APO12 | Riesgo | `registro-riesgos.md` |
| APO13, DSS05 | Seguridad | `../seguridad/` |
| APO14 | Datos | `../privacidad/inventario-datos.md` |
| APO10 | Proveedores | `proveedores.md` |
| BAI06 | Cambios | `../servicio/gestion-cambios.md` |
| DSS02, DSS04 | Incidentes y continuidad | `../servicio/` |
| MEA01, MEA03 | Medición y cumplimiento | `../mejora-continua/indicadores.md`, `matriz-cumplimiento.md` |

## Matriz de responsables

R = hace el trabajo. A = aprueba y responde. C = se le consulta. I = se le informa.
Reemplaza los roles por nombres del equipo. Cada fila tiene una sola A.

| Actividad | Líder de proyecto | Backend | Datos NASA | Seguridad y privacidad | Negocio |
|---|---|---|---|---|---|
| Aprobar alcance y planes | A | C | C | C | R |
| Aprobar un ADR | A | R | C | C | I |
| Programar una fase | I | R, A | C | C | I |
| Integrar fuentes de datos | I | C | R, A | C | I |
| Revisar seguridad de un cambio | I | C | I | R, A | I |
| Mantener inventario de datos | I | C | C | R, A | C |
| Desplegar a producción | A | R | I | C | I |
| Atender un incidente | A | R | C | R | I |
| Revisión de mejora continua | A | R | R | R | R |
