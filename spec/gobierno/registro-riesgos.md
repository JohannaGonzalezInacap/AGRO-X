# Registro de riesgos

Estado: Propuesta. Se revisa al cerrar cada fase. Probabilidad e impacto: bajo, medio, alto.

| # | Riesgo | Prob. | Impacto | Tratamiento | Dueño | Estado |
|---|---|---|---|---|---|---|
| R1 | El proyecto se aleja del reto (rotación) y pierde puntaje | Media | Alto | Rotación como núcleo y primera función en la demo | Líder | Abierto |
| R2 | Presentar datos de observación como si fueran pronóstico | Media | Alto | Fuente de pronóstico aparte y explicación clara (ADR-005) | Datos | Abierto |
| R3 | Umbrales agronómicos sin fuente dan recomendaciones erradas | Alta | Alto | Buscar fuente; marcar como ilustrativo lo no verificado | Datos | Abierto |
| R4 | Fuga de ubicación de parcelas o contactos | Baja | Alto | Controles del modelo de amenazas 5, 11 y 17 | Seguridad | Abierto |
| R5 | Activación de plan sin pago real | Baja | Alto | Verificación de webhook en tres pasos (ADR-003) | Backend | Abierto |
| R6 | Incumplir la Ley 21.719 al operar con datos reales | Media | Alto | Documentos de `privacidad/` y validación legal antes de abrir al público | Seguridad | Abierto |
| R7 | Una fuente externa cambia, limita o se cae | Media | Medio | Caché, tiempos de espera, adaptadores, error claro | Datos | Abierto |
| R8 | Licencia de la fuente de pronóstico no permite uso comercial | Media | Medio | Revisar licencia antes de elegir (Fase 0) | Datos | Abierto |
| R9 | Secreto subido al repositorio | Baja | Alto | `.gitignore`, escaneo automático, rotación inmediata si ocurre | Backend | Abierto |
| R10 | No alcanzar a terminar en el plazo | Alta | Medio | Mínimo de hackathon definido en `RUTA.md` | Líder | Abierto |
| R11 | Costos de nube inesperados | Baja | Medio | Alerta de presupuesto y escala a cero | Backend | Abierto |
| R12 | Código generado por un agente sin revisión humana | Media | Medio | Plan antes de código, pruebas obligatorias, revisión de cada cambio | Líder | Abierto |
