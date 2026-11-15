# ADR-015 — Despliegue en Render (reemplaza a ADR-004)

- Estado: Aceptada
- Fecha: 2026-11-15
- Reemplaza a: ADR-004 (quedaba en estado "Propuesta", nunca se aprobó)

## Contexto

ADR-004 proponía Google Cloud (Cloud Run + Cloud SQL) para el despliegue. Al llegar a la Fase 10
se verificó en vivo: el proyecto de GCP de Joha (`liajmk`) no tiene facturación activa, y ninguna
de sus cuentas de facturación está abierta actualmente (créditos vencidos). Sin facturación activa
no se puede crear ni Cloud Run ni una base de datos administrada en GCP — no es un problema de
código ni de permisos, es una condición de la cuenta.

Dado el tiempo disponible antes de la entrega (preocupación explícita de Joha), se decidió no
esperar a resolver la facturación de GCP y usar una plataforma que no la exija.

## Decisión

Desplegar en **Render** (`render.com`), sobre el workspace de Render que Joha ya tenía conectado
(donde también está su sitio de Atmósfera — son servicios independientes, uno no afecta al otro):

- Web service `agro-x-api`, contenedor construido desde el `Dockerfile` de este repositorio
  (imagen sin usuario root, Fase 10 de `RUTA.md`), plan gratis.
- Base de datos administrada `agro-x-db`, Postgres 16, plan gratis.
- Secretos (`JWT_SECRET`, `PAYMENT_WEBHOOK_SECRET`) generados por Render al crear el servicio
  (`generateValue: true` en `render.yaml`) — nunca pasan por el código ni por este chat.
- Despliegue automático: cada `git push` a `main` reconstruye y publica.

`app/core/db.py` gana `normalize_database_url()`: adapta la URL que entregue el proveedor
(`postgres://` o `postgresql://`) al driver psycopg3 que usa este proyecto. Esto es justamente lo
que permite cambiar de nube sin reescribir código (ADR-004, "Consecuencias").

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Render (elegida) | Ya conectado, no exige tarjeta para el nivel gratis, soporta contenedor + Postgres administrado | Sin región en Chile; el Postgres gratis expira a los 30 días y no tiene respaldo automático (ver `spec/servicio/continuidad-respaldo.md`) |
| Arreglar la facturación de GCP y seguir con ADR-004 | Cumple el plan original, región Santiago | Depende de una acción de Joha en la consola de Google (medio de pago) que no se podía resolver en el momento; se perdía tiempo antes de la entrega |
| Otra plataforma sin cuenta conectada (Fly.io, Railway, etc.) | Podrían ser igual de válidas | Habría que crear cuenta y conectar GitHub desde cero; Render ya estaba listo |

## Consecuencias

- `spec/servicio/continuidad-respaldo.md` se actualiza con la limitación real del plan gratis de
  Render (sin respaldo automático, expira a los 30 días) y una alternativa manual (`pg_dump`).
- `spec/gobierno/matriz-cumplimiento.md`: la fila de continuidad (ITIL) pasa de "Pendiente" a
  "Inicial, con una limitación conocida" — no se marca como cumplida de verdad hasta que haya un
  respaldo probado de verdad, aunque sea manual.
- Si el proyecto avanza más allá de la hackathon, hay que decidir entre: quedarse en Render con un
  plan pagado (Postgres con respaldo), o resolver la facturación de GCP y volver al plan original.
  Ambas rutas son viables porque el contenedor no cambia.
- Mercado Pago real sigue sin cuenta de pruebas (pendiente de Fase 0); el servicio desplegado usa
  `PAYMENT_PROVIDER=fake`, igual que en local. No es "producción" en el sentido de cobrar dinero
  real todavía — es la demo de la hackathon.

## Documentos relacionados

- ADR-004 (decisión original, ahora reemplazada)
- `render.yaml` (definición de la infraestructura)
- `spec/servicio/continuidad-respaldo.md`
- `spec/gobierno/matriz-cumplimiento.md`
- `docs/guion-de-demo.md`
