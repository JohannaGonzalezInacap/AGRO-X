# Brechas de datos personales

Estado: Propuesta. Plazos y destinatarios legales por validar.

Una brecha es cualquier acceso, pérdida o divulgación no autorizada de datos personales.

## Qué hacer

| Paso | Acción | Responsable |
|---|---|---|
| 1 | Avisar de inmediato al responsable de seguridad | Quien la detecte |
| 2 | Contener: revocar sesiones, rotar secretos, cerrar el acceso | Backend |
| 3 | Evaluar: qué datos, de cuántas personas, desde cuándo | Seguridad |
| 4 | Decidir si corresponde notificar a la autoridad y a los afectados | Líder, con apoyo legal |
| 5 | Notificar con lenguaje claro: qué pasó, qué datos, qué hacer | Líder |
| 6 | Corregir la causa | Backend |
| 7 | Análisis posterior sin culpables | Todo el equipo |

## Registro

Toda brecha, aunque sea menor, se anota en `../mejora-continua/postmortems/` con fecha, alcance,
causa, acciones y si se notificó.

## Pendiente

- [ ] Confirmar a quién y en qué plazo se notifica según la Ley 21.719.
- [ ] Definir el canal para que un usuario reporte un problema (ver `SECURITY.md`).
