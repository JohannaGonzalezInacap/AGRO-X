# Indicadores

Estado: Propuesta. Las metas son Ilustrativas; ajustarlas con los primeros datos reales.

| Indicador | Qué mide | Meta inicial | De dónde sale | Frecuencia |
|---|---|---|---|---|
| Disponibilidad | Porcentaje del tiempo con `/healthz` respondiendo | 99 % | Monitoreo | Mensual |
| Tiempo de respuesta | Rutas sin llamada externa | Menor a 500 ms | Métricas | Semanal |
| Alertas acertadas | Alertas que se cumplieron sobre el total emitido | Por definir | Comparar con lo observado después | Mensual |
| Anticipación | Días entre la alerta y el evento | 3 días o más | Alertas | Mensual |
| Recomendaciones entregadas | Uso del núcleo del reto | Creciente | Auditoría | Semanal |
| Incidentes | Cantidad por gravedad | 0 críticos | Registro de incidentes | Mensual |
| Tiempo de resolución | Desde que se registra hasta que se cierra | Según gravedad | Registro de incidentes | Mensual |
| Pagos fallidos | Pagos no aprobados sobre el total | Menor a 10 % | Tabla de pagos | Mensual |
| Solicitudes de privacidad en plazo | Exportaciones y eliminaciones atendidas a tiempo | 100 % | Auditoría | Mensual |
| Cambios revertidos | Despliegues que hubo que deshacer | Menor a 10 % | Historial de cambios | Mensual |
| Pruebas | Pruebas en verde en la rama principal | 100 % | Revisión automática | Cada cambio |
| Vulnerabilidades abiertas | Hallazgos altos del escaneo sin resolver | 0 | Revisión automática | Semanal |
