# Requisitos no funcionales

Estado: Propuesta. Las metas numéricas son Ilustrativas.

| Tema | Requisito | Cómo se comprueba |
|---|---|---|
| Seguridad | Todo tráfico por HTTPS | Configuración del despliegue |
| Seguridad | Controles de `seguridad/controles-aplicables.md` con prueba automática | `pytest` |
| Privacidad | Ningún dato personal en registros | Revisión y prueba |
| Rendimiento | Respuesta menor a 500 ms en rutas sin llamada externa | Medición en pruebas de carga simples |
| Rendimiento | Llamadas externas con tiempo de espera máximo de 15 s y caché | Prueba |
| Disponibilidad | Meta de 99 % mensual en demo | Monitoreo de `/healthz` |
| Resiliencia | Si una fuente externa falla, la API responde con error claro y no se cae | Prueba |
| Mantenibilidad | Cada módulo con `router`, `schemas`, `service` y sus pruebas | Revisión |
| Portabilidad | Corre en contenedor, sin depender de una nube específica | Imagen de contenedor |
| Trazabilidad | Cada respuesta lleva un identificador de solicitud | Prueba |
| Versionado | Rutas bajo `/v1` | Contrato |
