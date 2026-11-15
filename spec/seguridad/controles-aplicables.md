# Controles aplicables (borrador de declaración de aplicabilidad)

Estado: Propuesta. Alineado con los temas del Anexo A de ISO/IEC 27001:2022. Los números de control
deben confirmarse contra el texto oficial de la norma antes de citarlos en un informe.

No es una certificación. Es la lista de qué controles se adoptan, cuáles no y por qué.

| Tema | Control adoptado | Evidencia | Estado |
|---|---|---|---|
| Políticas | Reglas de seguridad en `CLAUDE.md` y este directorio | Documentos | Hecho |
| Roles y responsabilidades | Matriz de responsables | `gobierno/objetivos-y-raci.md` | Pendiente de nombres |
| Control de acceso | Roles, planes, filtro por dueño | Pruebas de acceso | Fase 2 y 3 |
| Autenticación | Argon2id, tokens cortos, renovación rotativa | Pruebas | Fase 2 |
| Criptografía | HTTPS en tránsito; cifrado en reposo del proveedor de base de datos | Configuración de la nube | Fase 10 |
| Desarrollo seguro | Validación de entrada, revisión de cambios, pruebas | Revisión automática | Fase 1 |
| Gestión de vulnerabilidades | Escaneo de dependencias y de código | Revisión automática | Fase 1 |
| Registro y monitoreo | Auditoría de acciones sensibles, identificador de solicitud | Tabla de auditoría | Fase 2 y 9 |
| Gestión de secretos | Variables de entorno y gestor de la nube | Configuración | Fase 1 y 10 |
| Proveedores | Registro y evaluación de proveedores | `gobierno/proveedores.md` | Hecho inicial |
| Incidentes | Procedimiento y plantilla de análisis posterior | `servicio/gestion-incidentes.md` | Hecho inicial |
| Continuidad | Respaldo y prueba de restauración | `servicio/continuidad-respaldo.md` | Fase 10 |
| Privacidad | Inventario, derechos, retención | `privacidad/` | Fase 9 |
| Seguridad física | No aplica: la infraestructura es del proveedor de nube | — | No aplica |
| Seguridad del personal | Fuera del alcance de la hackathon | — | No adoptado |

## Política de accesos (resumen)

- Cada persona del equipo usa su propia cuenta en la nube y en el repositorio. Sin cuentas compartidas.
- Segundo factor obligatorio en el repositorio, la nube y la pasarela de pago.
- Mínimo privilegio: solo quien despliega tiene permisos de producción.
- Los secretos de producción no se copian a equipos personales.
- Al salir alguien del equipo, se le quitan los accesos ese mismo día.
