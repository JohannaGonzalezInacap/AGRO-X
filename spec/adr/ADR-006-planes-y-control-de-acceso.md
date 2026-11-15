# ADR-006 — Planes y control de acceso por plan

- Estado: Propuesta
- Fecha: 2026-11-14

## Contexto
Hay tres planes con funciones distintas. El control debe estar en el servidor, porque una
aplicación cliente se puede modificar.

## Decisión
- Tres niveles ordenados: free, básico, pro.
- Cada ruta declara el plan mínimo que exige. Si no alcanza, responde 403 con `plan_required`.
- Un plan vencido se trata como free sin borrar nada.
- La diferencia entre planes se aplica de tres formas: acceso a rutas, frecuencia de actualización
  de alertas y nivel de detalle de la respuesta.
- El administrador no tiene restricción de plan.

## Consecuencias
- Cambiar qué incluye un plan es cambiar una tabla, no reescribir rutas.
- La tabla vigente vive en `spec/alcance-y-planes.md`.
