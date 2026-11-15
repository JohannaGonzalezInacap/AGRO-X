# Gestión de incidentes y problemas (ITIL)

Estado: Propuesta. Los tiempos son Ilustrativos.

Un **incidente** es algo que interrumpe o degrada el servicio ahora. Un **problema** es la causa de
fondo de uno o varios incidentes.

## Gravedad

| Nivel | Qué es | Ejemplo | Primera respuesta |
|---|---|---|---|
| Crítico | Datos o dinero en riesgo, o servicio caído | Fuga de datos, planes activados sin pago, API caída | 1 hora |
| Alto | Función principal no opera | Alertas o rotación fallan para todos | 4 horas |
| Medio | Función secundaria falla o hay rodeo | Listado de comerciantes lento | 1 día hábil |
| Bajo | Molestia menor | Texto equivocado | Próxima revisión |

## Pasos ante un incidente

1. **Registrar:** qué pasa, desde cuándo, a quién afecta.
2. **Clasificar** la gravedad.
3. **Contener:** volver a la versión anterior, desactivar la función o revocar accesos.
4. **Comunicar** al equipo y, si corresponde, a los usuarios.
5. **Resolver** y comprobar.
6. **Cerrar** con análisis posterior si fue crítico o alto (`../mejora-continua/postmortems/`).

Si involucra datos personales, seguir además `../privacidad/brechas.md`.

## Gestión de problemas

- Dos incidentes con la misma causa abren un problema.
- Cada problema tiene dueño, causa raíz y acción correctiva.
- La acción correctiva entra a `../mejora-continua/registro-mejoras.md`.

## Guías de operación

Los pasos para fallas conocidas van en `runbooks/`, un archivo por caso. Primeros a escribir en la
Fase 10: fuente externa caída, webhook de pago que no llega, restaurar respaldo, rotar un secreto.
