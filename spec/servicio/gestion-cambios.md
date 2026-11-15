# Gestión de cambios (ITIL: habilitación de cambios)

Estado: Propuesta.

## Flujo de un cambio

```
Rama nueva → Cambio + pruebas → Solicitud de cambio (pull request)
→ Revisión automática en verde → Revisión de otra persona → Fusión → Despliegue
```

## Tipos de cambio

| Tipo | Ejemplo | Quién aprueba |
|---|---|---|
| Estándar | Texto, documentación, prueba nueva | Una persona del equipo |
| Normal | Función nueva, cambio en una regla de negocio | Una persona, más actualización de `spec/` |
| Sensible | Autenticación, pagos, datos personales, permisos, infraestructura | Responsable de seguridad, además de la revisión normal |
| Urgencia | Corregir una falla en producción | Una persona; se documenta después en 24 horas |

## Reglas

1. Nada llega a la rama principal sin solicitud de cambio.
2. La revisión automática corre pruebas, estilo y escaneo de seguridad. En rojo no se fusiona.
3. Un cambio en base de datos lleva su migración y su forma de revertir.
4. Cada despliegue queda anotado en `CHANGELOG.md`.
5. El trabajo hecho por un agente de programación se revisa igual que el de una persona.
6. Si un despliegue falla, se vuelve a la versión anterior antes de investigar.
