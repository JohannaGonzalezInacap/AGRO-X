# Guion de demo — AGRO-X

## El link para el jurado

**https://agro-x-frontend.onrender.com** — ahí se abre la app de verdad (no Swagger ni `curl`),
conectada al backend real. Funciona en el celular: se puede "agregar a pantalla de inicio" desde
el navegador (Android: menú ⋮; iPhone: botón compartir). No es una instalación de tienda de apps,
es la misma página web con ícono propio — ver `frontend/README.md` para el detalle.

Entra con la cuenta **`juez-pro@example.com`** / **`JuecesAgroX2026`** (ver tabla de cuentas más
abajo) — ya tiene parcela y cultivo cargados, no hace falta registrar nada.

El resto de este documento es para probar la API directamente (`curl`/Swagger), pensado para
cuando quieras mostrar el backend en sí, no la app.

Hay **dos servidores de backend en pie**, con las **mismas dos cuentas de prueba** ya cargadas en
ambos — no hace falta registrar nada nuevo.

| Servidor | Base `<base>` | Para qué sirve | Limitación conocida |
|---|---|---|---|
| **Render** (real, ADR-015) | `https://agro-x-api.onrender.com` | Mostrar que está desplegado de verdad: cuentas, parcelas, rotación, pagos, privacidad | `POST /farms/{id}/alerts/refresh` falla (502): Open-Meteo no responde desde la red de Render (plan gratis). NASA POWER sí funciona ahí. |
| **Local + túnel temporal** | la URL de ngrok vigente (pregúntame si no la tienes a mano) | Todo lo anterior **más** alertas climáticas e ideas de venta urgente — ahí sí llegan ambas fuentes de datos | El túnel se cae si se reinicia; si no responde, avísame para levantarlo de nuevo |

## Cuentas de prueba (ya cargadas en los dos servidores)

| Cuenta | Correo | Contraseña | Plan | Parcela ya cargada |
|---|---|---|---|---|
| Pro | `juez-pro@example.com` | `JuecesAgroX2026` | Pro (hasta 2026-12-15) | "El Esperanza" (Maule, con riego), maíz en etapa cosecha |
| Free | `juez-free@example.com` | `JuecesAgroX2026` | Free | "Los Aromos" (Metropolitana, sin riego), trigo en floración |

Usa la cuenta **Pro** para la parte de alertas/ideas de venta (abajo) — ya tiene todo listo. La
cuenta **Free** sirve para mostrar el contraste (sin detalle de alerta, sin ideas de venta: 403
`plan_required`).

`GET /farms` con cada cuenta trae el `farm_id` que haga falta, pero por si se necesita a mano (son
distintos en cada servidor, aunque la parcela se llame igual):

| Parcela | `farm_id` en Render | `farm_id` en local/ngrok |
|---|---|---|
| El Esperanza (Pro) | `4afea516-29d8-4fee-b2db-b74a94d2c64f` | `12bb3519-3772-4642-bf78-796921cddc97` |
| Los Aromos (Free) | `4a0b0b50-938e-4675-8a12-1edd2f774efa` | `fca61cef-4385-4316-8685-2f6ce35a338b` |

(La alerta de severidad alta sembrada para la demo solo existe en **local/ngrok**, sobre "El
Esperanza" — en Render esa parcela no tiene alertas porque ahí el recálculo falla, ver tabla de
arriba.)

## 0. Antes de empezar

- Confirma que el servidor que vas a usar responde: `GET <base>/healthz` → `{"status":"ok"}`.
- Abre `<base>/docs` en el navegador — sirve de respaldo si algo falla en vivo con `curl`.
- En Render, **el primer request después de un rato de inactividad puede tardar ~30-50 segundos**
  ("cold start" del plan gratis). Haz ese primer `GET /healthz` *antes* de empezar a hablar.

## 1. Cuenta y parcela (1 min)

Usa la cuenta Pro ya cargada — no hace falta registrar nada:

```
POST /auth/login   { "email": "juez-pro@example.com", "password": "JuecesAgroX2026" }
GET  /farms        (con el access_token)  →  trae "El Esperanza" ya creada
```

Mensaje clave: "el rol y el plan los decide el servidor, nunca lo que mande el cliente".

## 2. Núcleo del reto: rotación de cultivos (2 min)

```
GET /crops
POST /farms/{farm_id}/rotation/recommendations   {}
```

(`farm_id` es el de "El Esperanza", que ya tiene registrado "maiz" en etapa "cosecha")

Mensaje clave: cada cultivo sugerido trae **sus razones** (nunca "porque sí"), qué tan ilustrativo
es el dato agronómico detrás, y la comparación **incluye quedarse con el cultivo actual**
(`is_current: true`) — tal como pide el enunciado del reto.

## 3. Alertas de riesgo climático e ideas de venta urgente (2 min) — usar el servidor local/ngrok

**Esta sección necesita el servidor local + ngrok**, no Render (ver tabla de arriba).

La parcela "El Esperanza" de la cuenta Pro ya tiene dos alertas activas cargadas — no hace falta
recalcular nada para la demo (recalcular trae el clima real del día, que puede o no disparar algo):

```
GET /farms/{farm_id}/alerts
```

Vas a ver dos: `crop_change` (porque el maíz está en etapa cosecha, con sugerencia de rotación) y
`frost` con `"severity": "alta"` — esta última se sembró a propósito para la demo (no es el clima
real de hoy; se nota porque `illustrative: true`, igual que el resto de los datos agronómicos del
proyecto). Con esa alerta de severidad alta activa, ahora sí responde con contenido:

```
GET /farms/{farm_id}/promotions/ideas
```

Mensaje clave: esta función **solo** responde si hay un riesgo real e inminente (severidad alta)
— por eso se sembró la alerta en vez de dejarlo al azar del clima del día de la demo. Si quieres
mostrar también el camino "sin riesgo", usa la parcela de la cuenta Free (`GET
/farms/{farm_id}/promotions/ideas` ahí da 403 `plan_required`, porque Free ni siquiera llega a
preguntar si hay riesgo).

Si quieres mostrar el recálculo real con el clima del día (opcional, con cualquiera de las dos
cuentas):

```
POST /farms/{farm_id}/alerts/refresh
```

Mensaje clave: combina NASA POWER (observado) y Open-Meteo (pronóstico); el detalle y las
recomendaciones solo aparecen en plan básico/pro (en free, solo tipo/gravedad/título). Si el clima
real no dispara nada nuevo, no borra lo que ya había — por eso la alerta sembrada sigue ahí.

## 4. Planes (1 min)

```
GET /billing/plans
POST /billing/checkout   { "plan": "pro" }
```

Mensaje clave: el plan **nunca** cambia solo por iniciar un pago — cambia cuando la pasarela
confirma por su cuenta (webhook firmado). Los precios de básico/pro siguen "por definir"
(`price_defined: false`) a propósito: no se inventa un número.

## 5. Privacidad (1 min, opcional si el tiempo aprieta)

```
GET /privacy/export   (con la cuenta Pro o Free, para mostrar que funciona)
```

**No uses `DELETE /privacy/account` con `juez-pro@example.com` ni `juez-free@example.com`** — son
las cuentas que van a usar los jueces, borrarla es irreversible. Si quieres mostrar el borrado en
vivo, regístrate una cuenta nueva y aparte solo para eso.

Mensaje clave: exportar y eliminar la cuenta ya están construidos (Ley 21.719), no solo
documentados.

## 6. Qué decir si preguntan por lo que falta

- **Marketplace de comerciantes y mermas**: construido y funciona, pero en pausa por decisión de
  negocio (ND-002) — no está claro todavía si vale la pena seguir invirtiendo ahí.
- **Precios reales, cuenta real de Mercado Pago**: pendientes, fuera del alcance de lo que se
  puede resolver en el tiempo de la hackathon.
- **Esta base de datos es gratuita y temporal** (expira a los 30 días, sin respaldo automático —
  ver `spec/servicio/continuidad-respaldo.md`). Si el proyecto sigue, pasa a un plan pagado o se
  resuelve el despliegue en Google Cloud (ADR-004/ADR-015).

## Respaldo manual de la base de datos (mientras el plan es gratis)

Antes de que se cumplan los 30 días desde que se creó `agro-x-db`, o antes de cualquier cambio
grande:

```
# La cadena de conexión "External" está en el panel de Render → agro-x-db → Connect.
pg_dump "postgresql://usuario:password@host/agro_x_db" > respaldo-agro-x-$(date +%Y%m%d).sql
```

Para restaurarlo en una base nueva (local o en Render):

```
psql "postgresql://usuario:password@host/nueva_db" < respaldo-agro-x-20261215.sql
```

## Si algo falla en vivo

- `GET <base>/healthz` da error o tarda mucho → probablemente el servicio estaba dormido; espera
  el cold start (hasta ~1 minuto) y reintenta.
- Un endpoint da 400 "Invalid host header" → el dominio desde donde se llama no está en
  `ALLOWED_HOSTS` (variable de entorno del servicio en Render).
- Cualquier otro error: todas las respuestas de error tienen `request_id` — anótalo, sirve para
  buscar el problema después sin tener que reproducirlo en vivo.
