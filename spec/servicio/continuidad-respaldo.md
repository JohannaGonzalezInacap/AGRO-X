# Continuidad y respaldo

Estado: Pendiente. Se completa en la Fase 10. Las metas son Ilustrativas.

## Metas

| Meta | Valor propuesto | Significado |
|---|---|---|
| Pérdida máxima de datos | 24 horas | Cuánto trabajo se puede perder como máximo |
| Tiempo máximo de recuperación | 4 horas | Cuánto puede estar caído el servicio |

## Respaldo

- Respaldo automático diario de la base de datos, administrado por la nube.
- Conservación: 30 días.
- Los respaldos están cifrados y con acceso restringido.
- El código y la documentación viven en el repositorio.
- Los secretos viven en el gestor de secretos, con registro de quién los cambia.

## Prueba de restauración

Un respaldo que nunca se probó no cuenta. Antes de abrir al público y luego cada tres meses:

- [ ] Restaurar el último respaldo en un entorno aparte.
- [ ] Comprobar que la API funciona con esos datos.
- [ ] Anotar cuánto tardó y qué falló en `../mejora-continua/revisiones/`.

## Escenarios

| Escenario | Respuesta |
|---|---|
| Cae una fuente externa | La API sigue; alertas con datos en caché o aviso de dato no disponible |
| Cae la pasarela de pago | Los planes vigentes siguen; no se venden nuevos |
| Despliegue defectuoso | Volver a la versión anterior |
| Pérdida de la base de datos | Restaurar el último respaldo |
| Secreto expuesto | Rotarlo de inmediato y revisar accesos |
