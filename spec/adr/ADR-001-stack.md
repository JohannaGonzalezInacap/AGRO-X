# ADR-001 — Stack tecnológico

- Estado: Propuesta
- Fecha: 2026-11-14

## Contexto
Hackathon con poco tiempo. El equipo conoce Python, pytest y VS Code. La API maneja datos
personales y pagos, así que la validación de entrada y las pruebas pesan mucho.

## Decisión
- Lenguaje: Python 3.12 o superior.
- Framework: FastAPI (valida la entrada y genera la documentación de la API automáticamente).
- Base de datos: PostgreSQL; SQLite en memoria solo para pruebas.
- Acceso a datos: SQLAlchemy 2. Migraciones: Alembic.
- Pruebas: pytest. Estilo: ruff.
- Empaquetado: contenedor Docker sin usuario root.
- Arquitectura: un solo servicio dividido en módulos (monolito modular).

## Alternativas consideradas
- Node.js con NestJS: válido, pero el equipo tiene menos práctica.
- Microservicios: demasiada operación para una hackathon.

## Consecuencias
- Un solo despliegue, fácil de entender y de probar.
- Si un módulo crece mucho, se puede separar después porque los módulos no se mezclan entre sí.
- Las versiones exactas de las librerías se fijan en la Fase 1.
