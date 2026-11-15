# AGRO-X

API de apoyo a decisiones para productores agrícolas, construida para una hackathon de la NASA.
Usa observaciones de la Tierra (NASA POWER) y pronóstico (Open-Meteo) junto con datos de la parcela
para recomendar rotaciones de cultivo que mejoren la salud del suelo y la resiliencia frente al
clima.

**Estado:** MVP en construcción por fases. Hoy están implementadas las Fases 1 a 5 de `RUTA.md`
(cuentas, parcelas, fuentes de datos externas y el motor de rotación — el núcleo del reto). Las
Fases 6 a 10 (alertas con control por plan, pagos, comerciantes y mermas, privacidad, despliegue)
todavía no están.

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
| `tests/` | Espejo de `app/modules/` más pruebas de integración y de seguridad |
| `migrations/` | Migraciones de base de datos (Alembic) |
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
