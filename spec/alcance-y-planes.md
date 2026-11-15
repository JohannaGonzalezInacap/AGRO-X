# Alcance y planes

Estado: Propuesta. Los precios y topes son Ilustrativos hasta que el equipo los fije.

## Dentro del alcance (versión hackathon)

- Cuentas con rol de productor o comerciante.
- Parcelas con datos de suelo e historial de cultivos.
- Recomendación de rotación de cultivos (núcleo del reto).
- Alertas de riesgo climático por parcela.
- Planes y pago con una pasarela.
- Listado de comerciantes y publicación de mermas (plan pro).
- Ideas de venta promocional ante una alerta (plan pro).

## Fuera del alcance por ahora

- Perfil de transportista.
- Inventario del productor.
- Aplicación móvil o web (esto es solo la API).
- Envío de notificaciones por correo, SMS o push.
- Compra y venta dentro de la plataforma (solo se conecta a las partes).

## Planes

| Función | Free | Básico | Pro |
|---|---|---|---|
| Parcelas | 1 | 3 | 20 |
| Recomendación de rotación | Sí | Sí | Sí |
| Actualización de alertas | Cada 30 días | Diaria | Cada 6 horas |
| Contenido de la alerta | Tipo, gravedad y título | Más detalle y recomendaciones por parcela | Igual que básico |
| Alerta de cambio de cultivo (ADR-008) | No | Sí, sin sugerencia de cultivo | Sí, con sugerencia de qué cultivo plantar |
| Ideas de promoción | No | No | Sí |
| Listado de comerciantes (lado productor) | No | No | Sí |
| Publicar mermas (lado productor) | No | No | Sí |
| Ver contacto de una merma (lado comerciante, ND-001) | No | No | Sí |
| Precio mensual | 0 | Por definir | Por definir |

**También se resolvió (ND-001):** cualquiera que use la app paga plan si quiere las funciones pro,
sin importar el rol — esto resuelve a la vez los puntos 2 y 4 de abajo. Un comerciante sin plan pro
puede ver el listado de mermas (producto, kilos, precio, región, uso, estado) pero no el contacto,
aunque el productor lo haya publicado; con pro, sí lo ve. Decidido 2026-11-15.

## Decisiones abiertas para el equipo

1. ¿La rotación va completa en free? Propuesta: sí, porque es lo que evalúa el reto.
2. ~~¿El comerciante paga plan o solo el productor?~~ Resuelto, ver ND-001 arriba.
3. Precios y moneda.
4. ~~¿Quién puede ver las mermas publicadas: cualquier comerciante o solo los de pago?~~ Resuelto,
   ver ND-001 arriba.
