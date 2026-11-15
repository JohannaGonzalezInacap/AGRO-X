# Matriz de cumplimiento

Estado: Propuesta. Regla: lo que diga "Pendiente" no se presenta como cumplido.

Esto muestra alineación, no certificación. Las obligaciones legales deben validarse con una persona
del área legal.

| Marco | Requisito (resumen) | Control en el proyecto | Evidencia | Estado |
|---|---|---|---|---|
| Ley 21.719 | Saber qué datos se tratan y para qué | Inventario de datos | `privacidad/inventario-datos.md` | Inicial |
| Ley 21.719 | Base de licitud y consentimiento | Consentimientos registrados | `privacidad/derechos-y-consentimiento.md` | Pendiente (Fase 9) |
| Ley 21.719 | Derechos del titular | Rutas de exportar y eliminar | `privacidad/derechos-y-consentimiento.md` | Pendiente (Fase 9) |
| Ley 21.719 | Seguridad y aviso de brechas | Procedimiento de brechas | `privacidad/brechas.md` | Inicial |
| Ley 21.719 | Guardar solo lo necesario y por el tiempo necesario | Política de retención | `privacidad/retencion-y-borrado.md` | Inicial |
| ISO/IEC 27001:2022 | Gestionar riesgos de seguridad | Registro de riesgos y modelo de amenazas | `gobierno/registro-riesgos.md` | Inicial |
| ISO/IEC 27001:2022 | Declarar controles aplicables | Tabla de controles | `seguridad/controles-aplicables.md` | Inicial |
| ISO/IEC 27001:2022 | Mejora continua | Ciclo de revisión | `mejora-continua/` | Inicial |
| ISO/IEC 27701:2025 | Gestión de privacidad | Carpeta de privacidad | `privacidad/` | Inicial |
| PCI DSS v4.0.1 | No tratar datos de tarjeta | Pago por redirección | `seguridad/pagos-pci.md` | Pendiente (Fase 7) |
| COBIT 2019 | Responsables definidos | Matriz de responsables | `gobierno/objetivos-y-raci.md` | Pendiente de nombres |
| COBIT 2019 | Proveedores gestionados | Registro de proveedores | `gobierno/proveedores.md` | Inicial |
| COBIT 2019 | Medición del desempeño | Indicadores | `mejora-continua/indicadores.md` | Inicial |
| ITIL | Cambios controlados | Flujo de cambios | `servicio/gestion-cambios.md` | Inicial |
| ITIL | Incidentes y problemas | Procedimiento | `servicio/gestion-incidentes.md` | Inicial |
| ITIL | Niveles de servicio | Catálogo por plan | `servicio/catalogo-y-niveles.md` | Inicial |
| ITIL | Continuidad | Respaldo probado | `servicio/continuidad-respaldo.md` | Inicial, con límite conocido: el plan gratis de la base de datos no tiene respaldo automático (ADR-015) |
| Datos NASA | Citar la fuente y respetar condiciones de uso | Cita en respuestas y documentación | `contratos/fuentes-datos.md` | Pendiente (Fase 4) |

"Inicial" significa que el documento existe con un primer contenido, pero aún no hay código ni
operación que lo respalde.
