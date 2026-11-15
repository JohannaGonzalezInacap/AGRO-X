# CLAUDE.md — Instrucciones para el agente

Este archivo lo lee Claude Code al abrir el proyecto. Manda sobre cualquier costumbre por defecto.

## Qué es este proyecto

API para una hackathon de la NASA. Reto: una herramienta de apoyo a decisiones que use observaciones
de la Tierra de la NASA, datos locales de suelo, características de cultivos y prioridades del
agricultor para explorar **rotaciones de cultivos** que mejoren la salud del suelo y la resiliencia.

Sobre ese núcleo, el equipo agrega: alertas de riesgo climático por parcela, ideas de venta
promocional para no perder cosecha, listado de comerciantes y venta de mermas, con tres planes de
pago (free, básico, pro). Perfiles: productor y comerciante ahora; transportista después.

El nombre definitivo del proyecto es **AGRO-X** (decidido 2026-11-15; antes "Agro-Xpace").

## Estado actual

Solo existe la estructura y la documentación. **No hay código todavía.** El trabajo se hace por fases,
en el orden de `RUTA.md`.

## Cómo se trabaja aquí (obligatorio)

1. **Documentación primero.** Antes de programar algo, debe estar descrito en `spec/`. Si falta o
   está ambiguo, primero propone el cambio en `spec/` y espera aprobación.
2. **Una fase a la vez.** No adelantes fases ni agregues funciones que nadie pidió.
3. **Plan antes de código.** Al empezar una fase, muestra el plan (archivos a crear y por qué) y
   espera el OK de Joha.
4. **Pruebas siempre.** Cada regla de negocio y cada control de seguridad lleva su prueba en `tests/`.
   Una fase termina solo con `pytest` en verde.
5. **Diario.** Al cerrar cada fase, agrega una entrada fechada en `DIARIO-DE-PROYECTO.md`: qué se
   hizo, qué se decidió, qué quedó pendiente.
6. **Decisiones.** Toda decisión técnica nueva o cambiada va como ADR en `spec/adr/`.
7. **Commits pequeños**, en español, con el formato `tipo: descripción` (feat, fix, docs, test, chore).

## Cómo explicarle a Joha

- En español, claro y sencillo, con ejemplos cotidianos. Sin rodeos ni elogios.
- Paso a paso, sin saltarse pasos ni asumir que algo ya se sabe. Di el porqué de cada acción.
- Tablas y diagramas cuando ayuden.
- Si algo no se pudo verificar, dilo.

## Stack (ver `spec/adr/ADR-001-stack.md`)

Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL (SQLite en memoria para pruebas), pytest,
ruff, Docker. Editor: VS Code. Entorno virtual en `.venv`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `spec/` | Fuente de verdad: dominio, contratos, BDD, ADR, seguridad, gobierno, privacidad, servicio, mejora continua |
| `app/core/` | Configuración, seguridad, autorización, middlewares, errores |
| `app/modules/<módulo>/` | `router.py` (rutas), `schemas.py` (entrada y salida), `service.py` (reglas) |
| `app/integrations/` | Clientes de datos externos (NASA, pronóstico, suelo) |
| `app/jobs/` | Tareas programadas |
| `tests/` | Espejo de `app/modules/` más pruebas de seguridad |
| `migrations/` | Migraciones de base de datos (Alembic) |
| `infra/` | Infraestructura como código |

## Reglas de seguridad (no negociables)

- Ningún secreto en el código ni en el repositorio. Todo por variables de entorno. No leas `.env`.
- Contraseñas con Argon2id. Nunca se registran ni se devuelven.
- Token de acceso de 15 minutos y refresh token de un solo uso (ver ADR-002).
- Toda consulta de datos de un usuario filtra por su dueño. Probar que un usuario no ve datos de otro.
- El rol y el plan los define el servidor. La entrada rechaza campos no esperados.
- El plan solo cambia desde un webhook de pago verificado. Nunca desde una solicitud del cliente.
- Datos de tarjetas: nunca pasan por esta API, ni por la base de datos, ni por los registros.
- Las URLs de servicios externos son fijas en la configuración. El usuario no elige a dónde se llama.
- A servicios externos se envían coordenadas redondeadas, nunca datos que identifiquen a la persona.
- Los registros no contienen datos personales, tokens ni contraseñas.
- Los errores usan el formato único de `spec/contratos/api-v1.md` y no exponen trazas.
- No desactives una prueba o un control para "que pase". Si estorba, se conversa.

## Privacidad y cumplimiento

Antes de agregar un dato personal nuevo, actualiza `spec/privacidad/inventario-datos.md`.
Antes de agregar un proveedor externo, actualiza `spec/gobierno/proveedores.md`.
Un riesgo nuevo va a `spec/gobierno/registro-riesgos.md`.

## Comandos

Con el entorno virtual activado (`.venv`):

| Qué | Comando |
|---|---|
| Instalar dependencias de desarrollo | `pip install -r requirements-dev.txt` |
| Correr la API en local | `uvicorn app.main:app --reload` |
| Probar | `pytest` |
| Revisar estilo | `ruff check .` |

## Definición de "terminado" para una fase

- [ ] Lo implementado coincide con `spec/` (o `spec/` se actualizó primero).
- [ ] `pytest` en verde, incluidas las pruebas de seguridad de la fase.
- [ ] `ruff` sin errores.
- [ ] Sin secretos ni datos personales en código, pruebas o registros.
- [ ] Entrada nueva en `DIARIO-DE-PROYECTO.md` y en `CHANGELOG.md`.
- [ ] Joha entendió qué se hizo y cómo probarlo.
