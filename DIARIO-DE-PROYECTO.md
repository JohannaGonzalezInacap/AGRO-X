
# Diario de proyecto

Una entrada por sesión de trabajo o por fase cerrada. Lo más nuevo arriba.

## 2026-11-15 — Corrección: la rotación compara también "quedarse" con el cultivo actual

**Qué pasó**
Al revisar el proyecto contra el enunciado del reto de la NASA, apareció una frase textual que el
motor de rotación no cumplía: "puede comparar al menos tres estrategias de rotación, **incluida
la actual**". El motor (Fase 5) hacía justo lo contrario a propósito: excluía el cultivo vigente
de la comparación porque "no tiene sentido rotar hacia lo que ya está plantado" — cierto para
"rotar", pero no es lo que pide el reto: ahí la "actual" es una estrategia más a comparar, no algo
a excluir.

**Hecho**
- `app/modules/rotation/service.py`: nueva función `_current_strategy_item` — evalúa "quedarse"
  con el cultivo vigente con las mismas reglas que una alternativa (familia repetida, alta demanda
  de agua con poca disponibilidad), y se agrega a la comparación marcado `is_current: true`.
- `RecommendationItem` (`schemas.py`) gana el campo `is_current`.
- `app/modules/alerts/service.py`: el aviso de "cambio de cultivo" (que es justo para avisar que
  conviene cambiar) ahora elige la primera sugerencia que **no** sea la actual, para no
  contradecirse a sí mismo sugiriendo quedarse igual.
- `spec/bdd/rotacion.feature`: dos escenarios nuevos. 3 pruebas nuevas/corregidas (antes 98, ahora
  100). `pytest` y `ruff check .` en verde.

**Verificado en local (no solo en pruebas)**
Se reinició el servidor que ven los jueces. Con una parcela con "maiz" vigente, la comparación
devolvió "maiz" con `is_current: true` y su propia razón ("seguir con este cultivo..."), compitiendo
en puntaje con las demás alternativas.

**Pendiente**
- El resto de la revisión contra el brief del reto (datasets de la NASA más allá de NASA POWER,
  glosario de términos científicos) quedó solo como hallazgo, no como tarea — son de alcance
  opcional según el propio enunciado, y ya estaban anotados como "Prioridad 2/3, dejar para
  después" en `spec/contratos/fuentes-datos.md`.
- Lo que ya quedó anotado en las entradas anteriores.

## 2026-11-15 — Fase 9: Privacidad y observabilidad (cerrada)

**Decidido (ND-003 y ADR-014, antes de programar)**
- `GET, PUT /privacy/consents` solo administra "comunicaciones promocionales". Los otros dos
  consentimientos de `spec/privacidad/derechos-y-consentimiento.md` ("publicar perfil de
  comerciante", "publicar contacto en una merma") ya los gobierna el propio
  `app/modules/marketplace/` (existencia del perfil; `Surplus.contact_visible`) — no se duplican
  en una tabla de consentimientos aparte, para no tener dos lugares que digan si algo está
  consentido.
- Al eliminar la cuenta: parcelas, historial de cultivo, alertas, perfil de comerciante, mermas
  propias y consentimientos se **borran**. Pagos y auditoría se **anonimizan** (se les quita el
  vínculo con la persona, el registro sigue existiendo) — así lo pide
  `spec/privacidad/retencion-y-borrado.md`. Para poder anonimizar un pago, `Payment.user_id` pasó a
  ser nullable (antes era obligatorio).
- "Registros sin datos personales" ya se cumplía: el único `logger` del proyecto
  (`app/jobs/alerts_job.py`) no registra nada personal. No hizo falta cambiar nada ahí.
- "Métricas para los indicadores": por ahora solo se asegura que exportar datos, cambiar un
  consentimiento y eliminar la cuenta queden en `AuditLog`, para que el indicador "Solicitudes de
  privacidad en plazo" (`spec/mejora-continua/indicadores.md`) tenga de dónde salir. Un tablero en
  vivo para el resto de los indicadores es trabajo de infraestructura, no de esta API.

**Hecho**
- `app/modules/privacy/`: modelo `Consent`, servicio y router con las 4 rutas del contrato
  (`GET /privacy/export`, `DELETE /privacy/account`, `GET/PUT /privacy/consents`).
- Migración nueva: tabla `consents` y `payments.user_id` ahora nullable. En SQLite, el cambio a
  nullable necesitó `batch_alter_table` (el autogenerado con `op.alter_column` directo falla:
  SQLite no soporta `ALTER COLUMN`).
- `GET /privacy/export` junta en un solo JSON el perfil, las parcelas con su historial de cultivo
  y sus alertas, el perfil de comerciante o las mermas propias según el rol, los pagos y los
  consentimientos — nunca el hash de la contraseña ni el de los tokens.
- `spec/dominio.md` gana el concepto "Consentimiento"; `spec/privacidad/inventario-datos.md` y
  `spec/privacidad/derechos-y-consentimiento.md` quedan al día con lo construido.
- `spec/bdd/privacidad.feature` nuevo. 8 pruebas nuevas en `tests/modules/privacy/`. (Antes 86,
  ahora 94 en total.) `pytest` y `ruff check .` en verde.

**Verificado en local (no solo en pruebas)**
- Se aplicó la migración a la base real y se reinició el servidor que ven los jueces. Con una
  cuenta de verificación: consentimiento no otorgado por defecto, se otorgó y quedó con fecha y
  versión, la exportación trajo el perfil y la parcela, y al eliminar la cuenta el login
  siguiente dio 401. Se aprovechó para limpiar de la base real una cuenta y parcela de prueba
  que había quedado de una verificación manual de una fase anterior (no era de un juez: correo
  `prod1@example.com`, creada hoy durante este mismo proyecto).

**Pendiente**
- Quedan en la base real otras 3 cuentas de prueba de fases anteriores
  (`pagos-real@example.com`, `comerciante-real@example.com`, `productor-real@example.com`) sin
  tocar — no es parte de esta fase, pero conviene que el equipo decida si se limpian antes de la
  entrega final.
- Lo que ya quedó anotado en las entradas anteriores (ND-002: decidir si el marketplace de mermas
  se retoma o se retira).

## 2026-11-15 — Corrección de alcance: ideas de venta urgente (ADR-013) y pausa del marketplace (ND-002)

**Qué pasó**
Después de cerrar la Fase 8, Joha aclaró que había entendido mal qué quería pausar: no eran las
"ideas de promoción", sino el marketplace de comerciantes y mermas en sí. Lo que ella sí quiere
activo es algo más puntual que un motor de marketing general: sugerirle al productor, de forma
creativa y realista, cómo vender su cosecha **cuando hay un riesgo real e inminente de perderla**
por el clima (una alerta activa de severidad alta) — no para toda la cosecha, en cualquier momento.

**Decidido (antes de programar, ver ADR-013 y ND-002)**
- ADR-013: `GET /farms/{id}/promotions/ideas` ya no está en pausa. Solo responde si la parcela
  tiene una alerta activa de severidad "alta" (si no, 404 `not_found`); requiere plan básico o pro,
  el mismo umbral que ver el detalle de una alerta. No depende del marketplace de mermas.
- ND-002 (`DECISIONES.md`, `spec/alcance-y-planes.md`): el marketplace de comerciantes y mermas de
  la Fase 8 queda **en pausa** — sigue construido y funcionando, pero no se invierte más ahí hasta
  que el equipo decida si de verdad es provechoso. `spec/bdd/marketplace.feature` se marcó
  `@en-pausa` en todos sus escenarios (sigue pasando, no se tocó el código).

**Hecho**
- `app/modules/promotions/`: `schemas.py` (`PromotionIdeaResponse`), `service.py`
  (`get_promotion_ideas`, sin tabla nueva: lee `Alert` y `CropHistory` que ya existían) y
  `router.py`. Registrado en `app/main.py`.
- `app/core/plans.py`: `PLANS_WITH_PROMOTION_IDEAS = {basic, pro}` y `promotion_ideas_allowed`.
- `spec/bdd/promociones.feature` nuevo (reemplaza el escenario `@en-pausa` que estaba en
  `alertas.feature`).
- 4 pruebas nuevas en `tests/modules/promotions/`. (Antes 82, ahora 86 en total.) `pytest` y
  `ruff check .` en verde.

**Verificado en local (no solo en pruebas)**
- Se reinició el servidor que ven los jueces. Con plan free: 403 `plan_required` sin tener que
  esperar una alerta. Con plan básico y sin alerta de severidad alta activa: 404 `not_found`. Con
  una alerta de severidad alta activa: 200 con las ideas de venta para esa alerta. Se borraron los
  datos de la cuenta usada para esta prueba de la base real al terminar.

**Pendiente**
- El equipo sigue sin decidir si el marketplace de mermas se retoma o se retira (ND-002).
- Lo que ya quedó anotado en las entradas anteriores.

## 2026-11-15 — Fase 8: Comerciantes y mermas (cerrada; ideas de promoción en pausa)

**Decidido (ND-001, antes de programar)**
- Resuelve dos preguntas que llevaban abiertas desde la Fase 0 en `spec/alcance-y-planes.md`
  ("¿el comerciante paga plan?" y "¿quién ve las mermas publicadas?"): cualquiera que use la app
  paga plan si quiere las funciones pro, sin importar el rol. Un comerciante sin pro ve el listado
  de mermas pero no el contacto, aunque el productor lo haya publicado. Documentado en
  `spec/alcance-y-planes.md` y en el nuevo índice `DECISIONES.md`.
- Las "ideas de promoción" (`GET /farms/{id}/promotions/ideas`) quedan **en pausa**, por decisión
  explícita de Joha: todavía no está claro qué debe hacer esa función. No se construyó nada de
  `app/modules/promotions/` esta fase. El escenario de `alertas.feature` que dependía de esto
  sigue marcado como diferido, ahora con la nota de que está en pausa, no solo pendiente de
  programar.

**Hecho**
- `app/modules/marketplace/`: `MerchantProfile` y `Surplus`, servicio y router con las 5 rutas del
  contrato.
- Listar comerciantes y publicar mermas (lado productor), y ver el contacto de una merma (lado
  comerciante, ND-001) quedan en `app/core/plans.py` junto con el resto del control por plan.
- El contacto de una merma solo aparece si se cumplen dos cosas a la vez: el productor la publicó
  con el contacto visible (dominio.md regla 7) y quien consulta es un comerciante pro (ND-001). El
  dueño de la merma siempre ve su propio contacto, sin esa restricción.
- Cambiar el estado de una merma es solo para su dueño (404 si no es tuya, mismo criterio que
  parcelas).
- `spec/bdd/marketplace.feature` nuevo (esta fase tampoco tenía uno, igual que la Fase 3).
- 10 pruebas nuevas en `tests/modules/marketplace/`. (Antes 72, ahora 82 en total.) `pytest` y
  `ruff check .` en verde.

**Verificado en local (no solo en pruebas)**
- Se reinició el servidor que ven los jueces (mismo puerto, mismo túnel) para traer el código.
  Perfil de comerciante creado, listado de mermas vacío, y un productor free recibió 403 al
  intentar publicar una merma — justo el criterio de "listo cuando" de `RUTA.md`.

**Pendiente**
- Lo que ya quedó anotado en las entradas anteriores.
- Nuevo: definir el alcance de "ideas de promoción" antes de poder construirlo.

## 2026-11-15 — Fase 7: Planes y pagos (cerrada)

**Hecho**
- `app/modules/billing/`: catálogo, inicio de pago, suscripción y webhook. Patrón adaptador
  (ADR-003) con `providers/base.py` (interfaz), `providers/fake.py` (simulada) y
  `providers/mercadopago.py` (real, modo de pruebas).
- Antes de programar, investigué el formato vigente de Mercado Pago (lo exige ADR-003): firma
  `x-signature` (`ts=...,v1=...`, `HMAC-SHA256` sobre `id:{data.id};request-id:{x-request-id};ts:{ts};`)
  y confirmación en `GET /v1/payments/{id}`. Los nombres de los campos de monto/moneda
  (`transaction_amount`, `currency_id`) no se confirmaron contra una respuesta real — ya era un
  pendiente de `spec/seguridad/pagos-pci.md`, no se agrega como nuevo.
- Webhook: firma inválida → 401; aviso repetido → 200 sin reaplicar nada (idempotencia por
  `provider` + `external_event_id`); monto distinto al esperado → no activa el plan y queda en
  auditoría (reusa `AuditLog` de la Fase 2); pago rechazado → plan sin cambios; pago aprobado con
  monto correcto → plan activo por 30 días.
- El adaptador real de Mercado Pago puede verificar firma y confirmar un pago, pero **no puede
  iniciar uno todavía**: falta la cuenta de pruebas (Fase 0) y el precio real de los planes
  (ADR-012). Queda listo el código para cuando ambos existan.
- ADR-012 (nuevo): un precio de desarrollo (básico 9.990 CLP, pro 19.990 CLP) para que el flujo de
  pago se pueda probar de punta a punta, mientras `spec/alcance-y-planes.md` siga sin un precio
  real. El catálogo público nunca lo muestra como si fuera definitivo (`price: null`).
- Endpoint de solo desarrollo (`POST /billing/_dev/fake-approve/{referencia}`) para simular a mano
  el resultado de la pasarela — deshabilitado si `PAYMENT_PROVIDER` no es `fake`.
- ADR-003 pasa a "Aceptada", con una sección de implementación.
- 9 pruebas nuevas en `tests/modules/billing/`, cubren los 8 escenarios de `pagos.feature`. (Antes
  63, ahora 72 en total.) `pytest` y `ruff check .` en verde.

**Verificado en local (no solo en pruebas)**
- Se reinició el servidor que ven los jueces (mismo puerto, mismo túnel) dos veces: una para
  completar `PAYMENT_WEBHOOK_SECRET` en el `.env` real (estaba vacío, mismo patrón que
  `JWT_SECRET` y `FORECAST_BASE_URL` en fases anteriores) y otra para tomar el código. Flujo
  completo con la pasarela simulada: catálogo, inicio de pago (el plan no cambia), aprobación
  simulada, webhook con firma válida activa `pro` por 30 días, webhook con firma falsa da 401.

**Pendiente**
- Lo que ya quedó anotado en las entradas anteriores. Se agrega: crear la cuenta de pruebas real
  de Mercado Pago y definir el precio real de básico/pro son tareas del equipo, no del agente
  (ambas bloquean que el adaptador real pueda cobrar de verdad).

## 2026-11-15 — Fase 6: Alertas y control por plan (cerrada)

**Hecho**
- `app/modules/alerts/`: modelo `Alert` (no se borra al dejar de aplicar, queda `active=False`,
  mismo criterio que el historial de cultivos), motor de riesgo y router con las 2 rutas del
  contrato.
- Motor de riesgo con 4 tipos (dominio.md regla 8): helada y calor extremo usan el pronóstico y la
  tolerancia del cultivo vigente (catálogo de la Fase 5); sequía usa humedad de suelo observada
  (NASA POWER) más lluvia pronosticada; lluvia intensa usa solo pronóstico.
- Alerta de cambio de cultivo (ADR-008): se dispara cuando el cultivo vigente llega a "cosecha".
  Free no la recibe; básico la recibe sin sugerencia; pro la recibe con la primera sugerencia del
  motor de rotación (Fase 5) y sus razones, o sin sugerencia si el motor no tiene con qué
  recomendar.
- Control por plan (`app/core/plans.py`, ampliado): frecuencia de recálculo (free 30 días, básico
  diario, pro cada 6 horas), detalle y recomendaciones ocultos en free. Recalcular antes de tiempo
  da 429 `too_soon` con la fecha en que se puede de nuevo.
- Si falla una fuente externa durante el recálculo, se responde 502 y **no se toca nada** de lo ya
  guardado — las alertas anteriores siguen disponibles, tal como pide `alertas.feature`.
- Job programado (`app/jobs/alerts_job.py`, `APScheduler`, corre dentro del mismo proceso):
  revisa cada hora qué parcelas ya pueden recalcularse según su plan. Si una parcela falla (fuente
  externa caída), se registra y se sigue con las demás, no se detiene el job completo.
- Migración nueva (`alerts`, más `alerts_refreshed_at` en `farms`).
- 11 pruebas nuevas en `tests/modules/alerts/`, cubren los 11 escenarios implementables de
  `alertas.feature`. (Antes 52, ahora 63 en total.) `pytest` y `ruff check .` en verde.

**Investigado antes de programar (pregunta de Joha)**
- Se buscó si alguna fuente gratuita (NASA u otra) da umbrales agronómicos de riesgo por cultivo.
  No se encontró ninguna usable hoy: FAO Ecocrop está retirada (sin API en vivo desde ~2015) y
  Meteoblue Crop Risk API está en Beta sin capa gratuita confirmada. NASA POWER da los datos
  observados, no los umbrales de riesgo — son dos cosas distintas. Decisión explícita de Joha:
  seguir con **datos dummy/ilustrativos** (ADR-011) para que el MVP quede funcional, y conectar una
  fuente real más adelante si el proyecto avanza.
- Único umbral no inventado: la helada meteorológica general (mínima ≤ 0 °C), una convención real.
  El ajuste según la tolerancia del cultivo sí es ilustrativo.

**Diferido**
- El escenario de `alertas.feature` sobre plan vencido e ideas de promoción depende de
  `GET /farms/{id}/promotions/ideas` (Fase 8); se marcó `@diferido-fase-8`.

**Verificado en local (no solo en pruebas)**
- Se reinició el servidor que ya tenían los jueces probando (mismo puerto, mismo túnel de ngrok —
  no cambió el link) para traer el código de la Fase 6. Con una parcela real: `refresh` llamó a
  NASA POWER y Open-Meteo reales sin error; salió sin alertas porque el clima actual de Santiago no
  dispara ninguna condición (correcto, no es un error); el segundo `refresh` inmediato dio 429
  `too_soon` como corresponde al plan free. El job programado arrancó sin errores en el log.

**Pendiente**
- Lo que ya quedó anotado en las entradas anteriores. Se amplía el pendiente de "fuente
  agronómica" para que incluya también los umbrales del motor de riesgo (antes solo cubría el
  catálogo de cultivos).

## 2026-11-15 — Segundo cambio de nombre y primer MVP público

**Decidido**
- El nombre definitivo del proyecto pasa a ser **AGRO-X** (antes "Agro-Xpace"). Se actualizó en
  `CLAUDE.md`, el título de la API (`app/main.py`) y `README.md`. Las carpetas del repositorio
  (`agro-xpace-kit/agro-xpace-api`) **no se renombraron** por la urgencia de la entrega — queda
  pendiente si se quiere más adelante, sin afectar en nada cómo lo descarga alguien desde GitHub.

**Hecho**
- Se reescribió `README.md`: ya no describe un "kit de arranque sin código", sino el estado real
  del proyecto (Fases 1 a 5 construidas) con instrucciones para clonar, instalar, migrar, correr y
  probar la API.
- Primer repositorio público en GitHub, para entregar con urgencia a la plataforma de la
  hackathon. Pensado para poder clonarse y correr en local (mismo patrón que "medreminder").

**Pendiente**
- Fases 6 a 10 de `RUTA.md` (alertas con control por plan, pagos, comerciantes/mermas, privacidad,
  despliegue). Se retoman después de esta entrega urgente.
- Todo lo que ya quedó anotado en entradas anteriores (fuente agronómica, catálogo de etapas,
  aprobaciones del equipo, plan de pago de Open-Meteo).

## 2026-11-14 — Fase 5: Recomendación de rotación de cultivos (cerrada)

**Hecho**
- `app/modules/rotation/`: catálogo (`Crop`), motor de puntaje (`service.py`) y router con
  `GET /crops` y `POST /farms/{id}/rotation/recommendations`.
- Reglas implementadas (las que sí prueba `rotacion.feature`): después de un cultivo que consume
  nitrógeno, las leguminosas (que lo fijan) puntúan más alto; repetir la familia de los dos
  últimos cultivos del historial penaliza; sin riego, con poca precipitación reciente y agua como
  prioridad más alta, los cultivos de alta demanda de agua bajan de puntaje. Toda recomendación
  trae al menos una razón y la lista de fuentes usadas.
- Migración con siembra de 8 cultivos (maíz, trigo, papa, tomate, lechuga, poroto, arveja,
  alfalfa) — ninguno con fuente agronómica todavía, así que `GET /crops` los marca a todos
  `illustrative: true` (pendiente desde la Fase 0).
- ADR-010 (nuevo): el umbral de "baja precipitación" que el `.feature` no fijaba (14 días, promedio
  menor a 2 mm/día de NASA POWER).
- 8 pruebas nuevas en `tests/modules/rotation/`, cubren los 6 escenarios del `.feature` con el
  clima simulado (sin red). (Antes 44, ahora 52 en total.) `pytest` y `ruff check .` en verde.

**Decidido (según lo que avisé en el plan, sin objeción)**
- Las prioridades "suelo" e "ingreso" se aceptan en la API pero todavía no afectan el puntaje —
  no hay regla de negocio definida para la primera, ni fuente de datos para la segunda (precios de
  mercado está fuera de alcance, `fuentes-datos.md`). La respuesta lo avisa en `notices` en vez de
  inventar una fórmula.
- El cultivo vigente de la parcela no se recomienda a sí mismo.
- Si falla la consulta al clima (502 de NASA POWER), la recomendación sigue devolviéndose sin ese
  dato, con un aviso — no se bloquea toda la respuesta por eso.

**Verificado en local (no solo en pruebas)**
- `uvicorn` + llamada real a NASA POWER (no simulada): tras registrar "maiz" como cultivo vigente,
  "poroto" y "arveja" (leguminosas) puntuaron más alto por la reposición de nitrógeno, y "papa",
  "tomate" y "lechuga" (alta demanda de agua) bajaron de puntaje porque la precipitación real
  reciente en Santiago resultó baja — confirma que el motor usa datos de clima reales, no solo los
  simulados de las pruebas.
- Se encontró que `curl | python -m json.tool` mostraba las tildes corruptas en esta máquina; se
  verificó con `httpx` directo que la respuesta del servidor tiene los bytes UTF-8 correctos — era
  un artefacto de esa combinación de herramientas en la terminal, no un bug de la API.

**Pendiente**
- Lo que ya quedó anotado en las entradas anteriores (fuente agronómica para el catálogo, catálogo
  de etapas, aprobaciones del equipo, alerta de cambio de cultivo de ADR-008, plan de pago de
  Open-Meteo).

## 2026-11-14 — Fase 4: Fuentes de datos (cerrada)

**Hecho**
- `app/integrations/nasa_power.py`: observaciones diarias (temperatura máx/mín, precipitación,
  humedad de suelo en zona de raíces). `app/integrations/forecast.py`: pronóstico diario de
  Open-Meteo (máx/mín, lluvia), tope de 16 días.
- `app/core/cache.py`: caché en memoria con vencimiento, reusable (mismo patrón que
  `rate_limit.py`). Evita repetir la misma consulta externa dentro de la ventana configurada.
- ADR-009 (nuevo): redondeo de coordenadas a 2 decimales y valor de relleno de NASA POWER (-999),
  ninguno de los dos estaba fijado en `spec/`.
- `httpx` pasó de dependencia de pruebas a dependencia de producción (ahora lo usan los clientes
  reales).
- 10 pruebas nuevas en `tests/integrations/`, todas con respuestas simuladas
  (`httpx.MockTransport`) — ninguna depende de internet. (Antes 34, ahora 44 en total.) `pytest` y
  `ruff check .` en verde.

**Verificado con una llamada real (no solo con las simuladas)**
- NASA POWER para Santiago (7 al 13 de noviembre de 2026): los dos días más recientes (12 y 13)
  volvieron sin dato, exactamente como avisa `spec/contratos/fuentes-datos.md` ("los días más
  recientes pueden venir sin dato") — y nuestro manejo del valor de relleno lo capturó bien.
- Open-Meteo para los próximos 4 días: respondió con datos completos.
- Se actualizó la fila de Open-Meteo en `spec/gobierno/proveedores.md` con la fecha de la
  verificación.

**Encontrado, no bloqueante (pero corregido)**
- `FORECAST_BASE_URL` en el `.env` real estaba vacío (plantilla de la Fase 1 sin completar, igual
  que pasó con `JWT_SECRET` en la Fase 2). Una variable vacía en `.env` pisa el valor por defecto
  de `Settings` — no es "ausente" para pydantic-settings. Se corrigió esa línea sin leer el resto
  del archivo, y además se fijó en `tests/conftest.py` (junto a `NASA_POWER_BASE_URL`) para que las
  pruebas no vuelvan a depender de que el `.env` local esté bien completado.

**Pendiente**
- Lo que ya quedó anotado en las entradas anteriores. Sigue sin resolverse (no le corresponde al
  agente): confirmar el plan de pago de Open-Meteo antes de cobrar a usuarios reales
  (`[COMPLETAR: ...]` en ADR-005 y en `proveedores.md`), y la atribución CC BY 4.0 — se resuelve
  cuando exista una ruta pública que muestre estos datos.

## 2026-11-14 — Fase 3: Parcelas e historial de cultivos (cerrada)

**Hecho**
- `app/core/plans.py`: tabla de topes por plan (fuente: `spec/alcance-y-planes.md`) y
  `effective_plan()` (un plan vencido se comporta como free, dominio.md regla 3). Se reutilizará en
  las Fases 6 y 7 para frecuencia de alertas y control de rutas.
- `app/core/time.py`: se sacó de `auth/service.py` el ajuste de zona horaria para SQLite (quedaba
  duplicado al necesitarlo también en `plans.py`).
- `app/modules/farms/`: modelos `Farm` y `CropHistory`, esquemas con `extra="forbid"`, servicio y
  router con las 6 rutas de `spec/contratos/api-v1.md`.
- `require_role()` nuevo en `app/modules/auth/service.py`: dependencia reutilizable para exigir un
  rol específico (aquí, "productor"; un comerciante recibe 403 `forbidden`).
- Registrar un cultivo nuevo vuelve no vigente al anterior (no lo borra); cambiar solo la etapa no
  crea un historial nuevo. Borrar una parcela borra su historial (`cascade`).
- Migración de Alembic nueva (`farms`, `crop_history`).
- `spec/bdd/farms.feature` nuevo: cubre creación, tope por plan, propiedad, rol, historial de
  cultivo. Se le movió el escenario de "no ver la parcela de otro" que había quedado diferido en
  `acceso.feature` desde la Fase 2.
- 14 pruebas nuevas en `tests/modules/farms/` (antes 20, ahora 34 en total). `pytest` y
  `ruff check .` en verde.

**Decidido (según lo que avisé en el plan, sin objeción)**
- Tope de parcelas superado responde `403 plan_required` (se reusa el código existente, no se
  inventó uno nuevo).
- El historial de cultivo no guarda una "temporada" como campo separado — `spec/dominio.md` la
  lista como atributo pero el contrato no define su formato ni la pide como entrada. Cada registro
  ya queda ubicado en el tiempo por `fecha_plantacion`, y `vigente` distingue la actual de las
  pasadas. Si el equipo define el formato más adelante, se agrega como ND.
- El cultivo del historial es texto libre, no una referencia al catálogo de cultivos (ese catálogo
  es de la Fase 5 y todavía no existe).

**Verificado en local (no solo en pruebas)**
- `uvicorn` + `curl` reales: registro, creación de parcela, tope de plan free (403 en la segunda),
  registro de cultivo, avance de etapa, y que un segundo productor no puede ver la parcela del
  primero (404).

**Pendiente**
- Lo que ya quedó anotado en las entradas anteriores (Fase 0, catálogo de etapas, fuente
  agronómica, aprobaciones del equipo, alerta de cambio de cultivo de ADR-008).

## 2026-11-14 — Fase 2: Cuentas y acceso (cerrada)

**Hecho**
- SQLAlchemy 2 + Alembic: `app/core/db.py` (engine, `Base`, `get_db`), primera migración
  (`migrations/versions/9f5d054ab8c9_crear_tablas_de_auth.py`) con `users`, `refresh_tokens`,
  `audit_log`.
- `app/core/security.py`: hash de contraseña con Argon2id, JWT de acceso (15 min, emisor y
  audiencia fijos), token de renovación opaco (se guarda solo su hash SHA-256).
- `app/core/rate_limit.py`: límite de intentos en memoria por IP y por acción (registro/login),
  ventana deslizante configurable.
- `app/modules/auth/`: modelos, esquemas (`extra="forbid"`, sin rol "admin" disponible), servicio
  y router con las 5 rutas de `spec/contratos/api-v1.md` (`register`, `login`, `refresh`, `logout`,
  `me`).
- Token de renovación de un solo uso: reutilizar uno ya usado revoca toda la cadena de la sesión
  (`family_id`), según ADR-002.
- 20 pruebas nuevas en `tests/modules/auth/` (antes 5, ahora 20 en total). `pytest` y
  `ruff check .` en verde.
- ADR-002 pasa a "Aceptada", con una sección "Implementación" que documenta el mecanismo elegido
  para el límite de intentos.
- Dependencias nuevas fijadas en `requirements.txt`: `sqlalchemy`, `alembic`, `psycopg[binary]`,
  `argon2-cffi`, `pyjwt`, `email-validator`.
- `pyproject.toml` nuevo: configura Ruff para no marcar `Depends()` de FastAPI como error (B008) y
  excluye `migrations/versions/` del lint (Alembic siempre genera ese estilo).

**Decidido (ADR-008, antes de empezar a programar la Fase 2)**
- Nueva función pedida por Joha: alerta de cambio de cultivo. Básico la recibe sin sugerencia; pro
  la recibe con la primera sugerencia del motor de rotación (Fase 5). Free no la recibe. Queda
  documentada en `spec/alcance-y-planes.md` y `spec/bdd/alertas.feature`; se implementa en las
  Fases 5 y 6, no en esta.

**Verificado en local (no solo en pruebas)**
- `uvicorn app.main:app --port 8010` + `curl` reales: registro, login, `/auth/me` con y sin token,
  renovación, reuso de un token ya usado (revoca la cadena), logout, límite de intentos (bloquea al
  superar 5 intentos por minuto).

**Encontrado, no bloqueante**
- Quedó un proceso de `uvicorn` de una sesión anterior escuchando en el puerto 8010 con código
  viejo; hubo que identificarlo (`netstat`) y cerrarlo antes de probar. Si vuelve a pasar, revisar
  procesos colgados antes de asumir que el código está mal.
- `JWT_SECRET` en el `.env` local estaba vacío (quedó como plantilla de la Fase 1). Se generó un
  valor aleatorio y se escribió directo en esa línea del `.env`, sin leer el resto del archivo
  (regla de `CLAUDE.md`). Si se despliega a otro entorno, hay que generar uno nuevo ahí también.
- `Settings.jwt_secret` pasó a ser obligatorio (sin valor por defecto): si falta, la API no arranca,
  en vez de fallar en silencio con una clave vacía.

**Diferido**
- El escenario de `acceso.feature` sobre no ver la parcela de otro depende de Parcela (Fase 3); se
  marcó `@diferido-fase-3` en el `.feature` y se mueve cuando esa fase arranque.
- Segundo factor de autenticación y almacén compartido para el límite de intentos (ambos ya
  anotados en ADR-002 como diferidos).

**Pendiente**
- Lo que ya quedó anotado en las entradas anteriores (Fase 0, catálogo de etapas, fuente
  agronómica, aprobaciones del equipo).

## 2026-11-14 — Fase 1: Esqueleto del proyecto (cerrada)

**Hecho**
- Se instaló Python 3.12.10 (solo había 3.11.9) y se creó `.venv` con esa versión, según ADR-001.
- `app/main.py` con FastAPI: `GET /healthz`, CORS con lista cerrada (`CORS_ORIGINS`),
  `TrustedHostMiddleware` (`ALLOWED_HOSTS`), middleware de `request_id` por solicitud, cabeceras de
  seguridad y límite de tamaño de cuerpo (413 a partir de 1 MiB). Formato único de error para 404,
  422, 413 y errores no previstos (`app/core/errors.py`), según `spec/contratos/api-v1.md`.
- Nuevo ADR-007 (`spec/adr/`): deja por escrito el límite de 1 MiB y las cabeceras elegidas, porque
  `spec/nfr.md` no fijaba el valor exacto.
- `requirements.txt` y `requirements-dev.txt` con versiones fijadas (`fastapi==0.163.0`,
  `uvicorn[standard]==0.54.0`, `pydantic-settings==2.16.3`; dev: `pytest==9.2.0`, `httpx==0.28.1`,
  `ruff==0.17.5`).
- 5 pruebas en `tests/` (healthz, formato de error en 404/422/413, cabeceras de seguridad). `pytest`
  y `ruff check .` en verde.
- `.github/workflows/ci.yml`: corre `ruff` y `pytest` en cada push/PR (acciones de GitHub fijadas
  por SHA, no por tag, para evitar que alguien les cambie el contenido después).
- Se completó la sección "Comandos" de `CLAUDE.md`.

**Verificado en local (no solo en pruebas)**
- `uvicorn app.main:app --port 8010` + `curl` reales a `/healthz` (200) y a una ruta inexistente
  (404 con el formato único de error).

**Encontrado, no bloqueante**
- El puerto 8000 está bloqueado por Windows en esta máquina (error de permisos del sistema
  operativo, no de la API). Usar otro puerto (ej. 8010) al correr `uvicorn` en local aquí.
- `starlette.testclient` avisa que usar `httpx` con él va a quedar obsoleto (sugiere `httpx2`). No
  afecta nada todavía; se revisa si sigue apareciendo en una fase futura.

**Pendiente**
- Lo que ya quedó anotado en las entradas anteriores (Fase 0, catálogo de etapas).

## 2026-11-14 — Cultivo por temporada en el historial de parcela

**Decidido**
- El registro de cuenta (Fase 2) sigue siendo solo correo/nombre/contraseña/rol: no se mezcla con
  datos de parcela. Localización, tipo de cultivo y hectáreas ya eran datos de **Parcela**;
  "vida de la planta" y "etapa actual" son nuevos y se agregaron al **Historial de cultivo**
  (`spec/dominio.md`, reglas 9 a 13):
  - Cada parcela tiene como máximo un cultivo **vigente** a la vez (el de la temporada actual).
  - La "vida de la planta" se guarda como fecha de plantación, no como número de años, para que la
    edad se calcule sola.
  - Catálogo de etapas (Ilustrativo, falta validar con fuente agronómica): `recien_plantada`,
    `crecimiento`, `floracion`, `fruto`, `cosecha`.
  - Las alertas y recomendaciones de rotación siempre usan el cultivo vigente de la parcela.
- Se actualizó `spec/contratos/api-v1.md`: `POST /farms/{id}/crop-history` registra el cultivo de
  la temporada (vuelve no vigente al anterior); se agregó `PATCH /farms/{id}/crop-history/current`
  para avanzar solo la etapa sin crear un historial nuevo.
- Se amplió la fila de "Datos de suelo y cultivos" en `spec/privacidad/inventario-datos.md`.

**Pendiente**
- Validar con fuente agronómica el catálogo de etapas (hoy Ilustrativo).
- Esto se implementa en la Fase 3 (`RUTA.md`), todavía no se programó nada.

## 2026-11-14 — Nombre definitivo

**Decidido**
- El nombre definitivo del proyecto es **Agro-Xpace** (ya no "AgroAlerta"). Se actualizó en
  `CLAUDE.md`, `README.md` y este diario. Las carpetas del repositorio se renombraron de
  `agroalerta-api-kit`/`agroalerta-api` a `agro-xpace-kit`/`agro-xpace-api`.

## 2026-11-14 — Avance de Fase 0

**Hecho**
- Se verificó con una llamada real que NASA POWER devuelve datos diarios válidos para Santiago
  (`T2M_MAX`, `T2M_MIN`, `PRECTOTCORR`), sin valores de relleno en el rango probado. Se documentó
  el resultado en `spec/contratos/fuentes-datos.md`.
- Se investigó y propuso una fuente de pronóstico (ADR-005): **Open-Meteo**. Cubre Chile, da hasta
  16 días de pronóstico, es gratis para desarrollo (10 000 llamadas/día, sin clave) y tiene plan de
  pago para producción comercial. Licencia CC BY 4.0 (exige atribución). Se descartó
  OpenWeatherMap por ahora (cifras de precio inconsistentes entre fuentes de terceros) y no se
  encontró API pública de la Dirección Meteorológica de Chile.
- Se actualizó `spec/gobierno/proveedores.md` con el estado de NASA POWER y la propuesta de
  Open-Meteo.

**Sigue pendiente de decisión del equipo (no lo resuelve el agente)**
- Aprobar o corregir ADR-001 a ADR-006 y `alcance-y-planes.md` (hoy en estado "Propuesta").
- Aprobar la propuesta de fuente de pronóstico (Open-Meteo) en ADR-005.
- Crear cuenta de pruebas en la pasarela de pago (Mercado Pago, ADR-003).
- Elegir la nube y crear la cuenta (Google Cloud propuesto, ADR-004).
- Repartir responsabilidades con nombres reales en `spec/gobierno/objetivos-y-raci.md`.
- Validar con el área legal lo relativo a la Ley 21.719 (sigue pendiente de la entrada anterior).
- Conseguir fuente agronómica para el catálogo de cultivos (sigue pendiente de la entrada anterior).

## 2026-11-14 — Estructura inicial

**Hecho**
- Se definió la idea: API con perfiles (productor, comerciante; transportista después) y planes
  (free, básico, pro).
- Se creó la estructura de carpetas y la documentación inicial en `spec/`.
- Se revisó la alineación con COBIT 2019, ITIL, ISO/IEC 27001, ISO/IEC 27701, PCI DSS y Ley 21.719.

**Decidido (como propuesta, falta confirmar con el equipo)**
- Stack: Python, FastAPI, PostgreSQL (ADR-001).
- El módulo de rotación de cultivos es el núcleo, porque es lo que pide el reto.
- Los datos de la NASA son observación; el pronóstico viene de otra fuente (ADR-005).
- El pago ocurre en la página de la pasarela; la API nunca ve tarjetas (ADR-003).

**Pendiente**
- Toda la Fase 0 de `RUTA.md`.
- Validar con alguien del área legal lo relativo a la Ley 21.719.
- Conseguir fuente agronómica para el catálogo de cultivos.
