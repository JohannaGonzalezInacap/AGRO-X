# Guion de demo — AGRO-X

Pensado para una demo corta (5-8 minutos) con `curl`/Swagger contra el servicio desplegado en
Render (ADR-015). Reemplaza la URL `<base>` por la del servicio real (`agro-x-api.onrender.com` o
la que Render haya asignado — revisar en `render.yaml` / panel de Render si cambió).

## 0. Antes de empezar

- Confirma que el servicio responde: `GET <base>/healthz` → `{"status":"ok"}`.
- Abre `<base>/docs` en el navegador — sirve de respaldo si algo falla en vivo con `curl`.
- **El primer request después de un rato de inactividad puede tardar ~30-50 segundos**: el plan
  gratis de Render apaga el servicio cuando nadie lo usa y lo despierta en la primera llamada
  ("cold start"). Haz ese primer `GET /healthz` *antes* de empezar a hablar, no durante la demo.

## 1. Cuenta y parcela (1 min)

```
POST /auth/register   { "email": "demo@agro-x.cl", "name": "Demo", "password": "demo-hackathon-2026", "role": "producer" }
POST /auth/login       { "email": "demo@agro-x.cl", "password": "demo-hackathon-2026" }
POST /farms  (con el access_token)
  { "name": "Parcela Demo", "region": "Metropolitana", "latitude": -33.45, "longitude": -70.65,
    "area_hectares": 3.0, "soil_texture": "franco", "has_irrigation": true }
```

Mensaje clave: "el rol y el plan los decide el servidor, nunca lo que mande el cliente".

## 2. Núcleo del reto: rotación de cultivos (2 min)

```
GET /crops
POST /farms/{farm_id}/crop-history   { "crop": "maiz", "planting_date": "2026-01-10", "stage": "cosecha" }
POST /farms/{farm_id}/rotation/recommendations   {}
```

Mensaje clave: cada cultivo sugerido trae **sus razones** (nunca "porque sí") y qué tan ilustrativo
es el dato agronómico detrás.

## 3. Alertas de riesgo climático (2 min)

```
POST /farms/{farm_id}/alerts/refresh
GET  /farms/{farm_id}/alerts
```

Mensaje clave: combina NASA POWER (observado) y Open-Meteo (pronóstico); el detalle y las
recomendaciones solo aparecen en plan básico/pro (en free, solo tipo/gravedad/título).

Si el clima real no dispara ninguna alerta ese día (puede pasar, depende del clima real de la
región elegida): explicar que es esperado — el motor no inventa riesgo que no existe — y mostrar
`GET /farms/{farm_id}/promotions/ideas` devolviendo 404 `not_found` como prueba de que tampoco
inventa ideas de venta sin un riesgo real detrás (ADR-013).

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
GET /privacy/export
DELETE /privacy/account   (con la cuenta de demo, al final — es irreversible)
```

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
