# Continuidad y respaldo

Estado: Inicial, con una limitación conocida (Fase 10, ADR-015). Las metas son Ilustrativas.

## Metas

| Meta | Valor propuesto | Significado |
|---|---|---|
| Pérdida máxima de datos | 24 horas | Cuánto trabajo se puede perder como máximo |
| Tiempo máximo de recuperación | 4 horas | Cuánto puede estar caído el servicio |

## Respaldo — situación real en la demo (Render, plan gratis)

**El plan gratis de Postgres en Render no incluye respaldo automático**, y la base de datos
**expira a los 30 días de creada** (no hay forma de extenderlo sin pasar a un plan pagado). Esto
es una limitación real del nivel gratis, documentada por el propio proveedor — no se promete un
respaldo que no existe (regla del encabezado de este documento: lo que diga "Pendiente" no se
presenta como cumplido).

- Mientras se esté en el plan gratis: respaldo **manual** con `pg_dump` antes de cualquier cambio
  grande o, como mínimo, antes de que se cumplan los 30 días (`docs/guion-de-demo.md` tiene el
  comando exacto).
- El código y la documentación viven en el repositorio (eso sí es automático: cada commit es, en
  los hechos, un respaldo del código).
- Los secretos (`JWT_SECRET`, `PAYMENT_WEBHOOK_SECRET`) los genera Render al crear el servicio y
  viven en su panel de variables de entorno, no en el código ni en este chat.
- Si el proyecto sigue después de la hackathon y se pasa a un plan pagado de Render (o se resuelve
  la facturación de GCP y se vuelve a ADR-004), Render ofrece respaldo lógico con retención
  limitada y recuperación a un punto en el tiempo — ahí sí se puede marcar esta fila como cumplida
  de verdad.

## Prueba de restauración

Un respaldo que nunca se probó no cuenta. Mientras se esté en el plan gratis (sin respaldo
automático), esto se reduce a probar que el `pg_dump` manual de verdad se puede restaurar:

- [ ] Restaurar el último `pg_dump` en una base aparte (puede ser local, con Docker).
- [ ] Comprobar que la API arranca y responde con esos datos.
- [ ] Anotar cuánto tardó y qué falló en `../mejora-continua/revisiones/`.

Con un plan pagado (respaldo automático de verdad), la prueba pasa a ser trimestral, como decía la
versión anterior de este documento.

## Escenarios

| Escenario | Respuesta |
|---|---|
| Cae una fuente externa | La API sigue; alertas con datos en caché o aviso de dato no disponible |
| Cae la pasarela de pago | Los planes vigentes siguen; no se venden nuevos |
| Despliegue defectuoso | Volver a la versión anterior |
| Pérdida de la base de datos | Restaurar el último respaldo |
| Secreto expuesto | Rotarlo de inmediato y revisar accesos |
