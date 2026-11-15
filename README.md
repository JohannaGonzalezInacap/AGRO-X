# AGRO-X

API de apoyo a decisiones para productores agrícolas, construida para una hackathon de la NASA.
Usa observaciones de la Tierra (NASA POWER) y pronóstico (Open-Meteo) junto con datos de la parcela
para recomendar rotaciones de cultivo que mejoren la salud del suelo y la resiliencia frente al
clima.

**Estado:** las 10 fases de `RUTA.md` están cerradas. Desplegado en Render (ADR-015); el único
pendiente real de negocio es el marketplace de mermas, que quedó en pausa (ND-002) hasta que el
equipo decida si vale la pena seguir invirtiendo ahí.

## Qué hace hoy

- **Cuentas**: registro, login, renovación de sesión, cierre de sesión, perfil propio. Roles
  productor/comerciante. Contraseñas con Argon2id, tokens de acceso de 15 minutos.
- **Parcelas**: crear, ver, editar, borrar; tope de parcelas según el plan (free/básico/pro);
  historial de cultivos con etapa actual.
- **Fuentes de datos**: clientes de NASA POWER (observación) y Open-Meteo (pronóstico), con caché,
  tiempos de espera y manejo de datos faltantes.
- **Rotación de cultivos**: catálogo de cultivos y motor de recomendación que puntúa cada cultivo
  con razones explicadas (reposición de nitrógeno, evitar repetir familia, demanda de agua según
  el clima reciente de la parcela).
- **Alertas de riesgo climático**: helada, calor extremo, sequía, lluvia intensa y aviso de cambio
  de cultivo; frecuencia y detalle según el plan; job programado que recalcula sola cada parcela.
- **Ideas de venta urgente**: sugerencias ante una alerta de riesgo alto (ADR-013).
- **Planes y pagos**: catálogo de planes, checkout, webhook verificado (pasarela simulada en
  desarrollo; Mercado Pago real pendiente de cuenta de pruebas).
- **Comerciantes y mermas**: construido y funcional, pero **en pausa** por decisión de negocio
  (ND-002) — no se promueve como función confirmada del producto.
- **Privacidad**: exportar mis datos, eliminar mi cuenta (borra lo propio, anonimiza pagos y
  auditoría), consentimientos.
- **Despliegue**: contenedor sin usuario root, Render (web service + Postgres administrado),
  secretos generados por la plataforma (ADR-015, reemplaza a ADR-004/Google Cloud).

Ver `spec/contratos/api-v1.md` para el contrato completo de rutas, y `DIARIO-DE-PROYECTO.md` para
la bitácora detallada de qué se construyó en cada fase y qué decisiones se tomaron.

## Cómo correrlo en tu máquina

Necesitas Python 3.12 o superior.

```bash
git clone <URL-de-este-repositorio>
cd agro-x-api   # o el nombre de la carpeta que te quedó al clonar

python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements-dev.txt

# Windows:
copy .env.example .env
# macOS / Linux:
cp .env.example .env
```

Abre `.env` y completa al menos `JWT_SECRET` con un valor largo y aleatorio (no reutilices el de
otro proyecto). El resto de las variables ya trae valores por defecto razonables para desarrollo
local (base de datos SQLite, fuentes de datos externas).

Aplica las migraciones y levanta el servidor:

```bash
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

La API queda en `http://localhost:8000`. La documentación interactiva (Swagger) está en
`http://localhost:8000/docs` — ahí puedes probar cada ruta desde el navegador, sin necesitar
`curl`.

### Probar que funciona

```bash
curl http://localhost:8000/healthz
```

Debe responder `{"status":"ok"}`. Para un recorrido completo (crear cuenta, iniciar sesión,
registrar una parcela y pedir una recomendación de rotación), usa `/docs` o revisa los ejemplos de
`curl` en `DIARIO-DE-PROYECTO.md` (cada fase cerrada incluye los que se usaron para verificarla).

### Correr las pruebas automáticas

```bash
pytest
ruff check .
```

Ninguna prueba depende de internet: las llamadas a NASA POWER y Open-Meteo están simuladas.

## Estructura del proyecto

| Carpeta | Contenido |
|---|---|
| `spec/` | Fuente de verdad: dominio, contratos, BDD, decisiones de arquitectura (ADR), seguridad, gobierno, privacidad |
| `app/core/` | Configuración, seguridad, autorización, middlewares, errores, caché |
| `app/modules/<módulo>/` | `router.py` (rutas), `schemas.py` (entrada y salida), `service.py` (reglas), `models.py` |
| `app/integrations/` | Clientes de datos externos (NASA POWER, Open-Meteo) |
| `app/jobs/` | Tareas programadas (recálculo de alertas) |
| `tests/` | Espejo de `app/modules/` más pruebas de integración y de seguridad |
| `migrations/` | Migraciones de base de datos (Alembic) |
| `docs/guion-de-demo.md` | Guion paso a paso para mostrar la API en vivo |
| `render.yaml`, `Dockerfile` | Infraestructura del despliegue (ADR-015) |
| `DIARIO-DE-PROYECTO.md` | Bitácora fechada: qué se hizo, qué se decidió, qué quedó pendiente |
| `CHANGELOG.md` | Historial de cambios por fase |
| `CLAUDE.md` | Reglas que sigue el agente de IA que ha construido este proyecto junto con el equipo |

## Seguir construyendo (equipo)

El proyecto sigue un flujo de documentación-primero: antes de programar algo nuevo, se describe en
`spec/`. `RUTA.md` tiene las fases pendientes, en orden, con el texto exacto para pedirle cada una
a Claude Code. `CLAUDE.md` tiene las reglas de seguridad y de trabajo que no son negociables.

## Antes de una demo o entrega pública

Revisa `spec/gobierno/matriz-cumplimiento.md` y los marcadores `[COMPLETAR: ...]` que sigan
abiertos en `spec/adr/` y `spec/gobierno/proveedores.md` — son decisiones reales que el equipo
todavía no ha tomado (por ejemplo, el plan de pago de la fuente de pronóstico). No se presentan
como resueltas.
