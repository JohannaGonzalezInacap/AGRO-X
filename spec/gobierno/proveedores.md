# Proveedores

Estado: Propuesta. Completar en la Fase 0. Agregar una fila antes de integrar cualquier servicio nuevo.

| Proveedor | Servicio | Qué datos recibe | Datos personales | Condiciones revisadas | Plan si falla |
|---|---|---|---|---|---|
| NASA POWER | Clima y agroclimatología | Coordenadas redondeadas | No | Llamada real verificada (2026-11-14); falta revisar política de uso y cita formal | Usar caché; avisar dato no disponible |
| Open-Meteo (propuesto para pronóstico) | Pronóstico diario y horario | Coordenadas redondeadas | No | Llamada real verificada (2026-11-14); licencia CC BY 4.0 (exige atribución); plan gratis solo para desarrollo, [COMPLETAR: CONFIRMAR PLAN DE PAGO ANTES DE PRODUCCIÓN] | Alerta solo con datos observados, marcada como parcial |
| Pasarela de pago (Mercado Pago propuesto) | Cobro de planes | Monto, referencia, correo del pagador | Sí | Pendiente (contrato, PCI) | Planes vigentes siguen; no se venden nuevos |
| Nube (Google Cloud propuesto) | Cómputo, base de datos, secretos | Todos | Sí | Pendiente (acuerdo de tratamiento de datos, región) | Respaldo y contenedor portable |
| GitHub | Código y revisión automática | Código | No | Pendiente | Copia local del repositorio |
| Agente de programación (Claude Code) | Asistencia de desarrollo | Código y documentación | No debe recibir datos reales | Pendiente | Desarrollo manual |

## Reglas

1. Ningún proveedor recibe más datos de los que necesita.
2. Datos reales de usuarios no se usan en pruebas ni se pegan en herramientas de asistencia.
3. Antes de producción: revisar dónde guarda datos cada proveedor que recibe datos personales.
